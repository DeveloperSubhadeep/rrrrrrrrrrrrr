#Thanks @dreamxbotz for helping in this journey 

import jinja2
from info import *
from dreamxbotz.Bot import dreamxbotz
from dreamxbotz.util.human_readable import humanbytes
from dreamxbotz.util.file_properties import get_file_ids
from dreamxbotz.server.exceptions import InvalidHash
import urllib.parse
import logging
import aiohttp


async def render_page(id, secure_hash, src=None):
    file = await dreamxbotz.get_messages(int(BIN_CHANNEL), int(id))
    file_data = await get_file_ids(dreamxbotz, int(BIN_CHANNEL), int(id))
    if file_data.unique_id[:6] != secure_hash:
        logging.debug(f"link hash: {secure_hash} - {file_data.unique_id[:6]}")
        logging.debug(f"Invalid hash for message with - ID {id}")
        raise InvalidHash

    src = urllib.parse.urljoin(
        URL,
        f"{id}/{urllib.parse.quote_plus(file_data.file_name)}?hash={secure_hash}",
    )


    # **NEW**: This is the link to your new download page
    download_page_url = urllib.parse.urljoin(
        URL,
        f"download/{id}/{urllib.parse.quote_plus(file_data.file_name)}?hash={secure_hash}",
    )



    tag = file_data.mime_type.split("/")[0].strip()
    file_size = humanbytes(file_data.file_size)
    if tag in ["video", "audio"]:
        template_file = "dreamxbotz/template/req.html"
    else:
        template_file = "dreamxbotz/template/dl.html"
        # async with aiohttp.ClientSession() as s:
        #     async with s.get(src) as u:
        #         file_size = humanbytes(int(u.headers.get("Content-Length")))


        try:
            async with aiohttp.ClientSession() as s:
                async with s.get(src) as u:
                    file_size = humanbytes(int(u.headers.get("Content-Length")))
        except Exception:
            logging.warning("Could not fetch Content-Length for non-video/audio file.")


    with open(template_file) as f:
        template = jinja2.Template(f.read())

    file_name = file_data.file_name.replace("_", " ")

    return template.render(
        file_name=file_name,
        file_url=src,
        file_size=file_size,
        file_unique_id=file_data.unique_id,
        download_page_url=download_page_url,  # <-- Pass the new URL to the template
    )



async def render_download_page(id, secure_hash):
    """
    **NEW FUNCTION**
    Renders the dedicated download page (download.html).
    """
    try:
        file_data = await get_file_ids(dreamxbotz, int(BIN_CHANNEL), int(id))
    except Exception:
        raise FIleNotFound

    if file_data.unique_id[:6] != secure_hash:
        logging.debug(f"Invalid hash for message with - ID {id}")
        raise InvalidHash

    # This is the actual direct download URL the browser will use
    actual_download_url = urllib.parse.urljoin(
        URL,
        f"{id}/{urllib.parse.quote_plus(file_data.file_name)}?hash={secure_hash}",
    )
    
    # Prepare context for the download.html template
    file_name = file_data.file_name.replace("_", " ")
    total_size_bytes = file_data.file_size
    total_size_formatted = humanbytes(total_size_bytes)
    file_type = file_data.mime_type or "Unknown"

    # Load and render the download.html template
    # IMPORTANT: Make sure download.html is in the same directory as your other templates.
    template_file = "dreamxbotz/template/download.html"
    with open(template_file) as f:
        template = jinja2.Template(f.read())

    return template.render(
        file_name=file_name,
        total_size_bytes=total_size_bytes,
        actual_download_url=actual_download_url,
        file_type=file_type,
        total_size_formatted=total_size_formatted,
    )
