#!/usr/bin/env python
# coding=utf-8
'''
File Description:
Author          : CHEN, JIA-LONG
Create Date     : 2024-06-17 14:00
FilePath        : \\module.py
Copyright © 2024 CHEN JIA-LONG.
'''

import asyncio
import ctypes
import logging
import os
import re
import time
import tkinter as tk
from datetime import datetime, timedelta
from tkinter import filedialog
from typing import Any, Coroutine, List, Optional, Tuple

import pandas as pd
import telnetlib3
from aioconsole.stream import aprint


def select_folder(windows_title: str = "Select Folder", path_arg: str = None) -> str:
    """
    Open a dialog for the user to select a folder and return the folder's absolute path.
    If a path argument is provided, use it after validation and normalization.

    Args:
        windows_title (str): The title of the folder selection dialog.
        path_arg (str): The folder path provided as an argument.

    Returns:
        str: The absolute path of the selected or provided folder.

    Raises:
        ValueError: If the user cancels the folder selection or if the path argument is invalid.
    """

    def valid_path(path) -> bool:
        """Check if a path is valid and can be created if it does not exist."""
        try:
            # Ensure path is absolute and normalized, Check for invalid characters on Windows
            if not os.path.isabs(path) or re.search(r'[*?"<>|]', path):
                return False
            if not os.path.exists(path):
                os.makedirs(path)
            return True
        except OSError as e:
            logging.error(f"Error creating directory {path}: {e}")
            return False

    if path_arg:
        # Normalize the path to ensure it is in a standard format
        folder_path = os.path.normpath(path_arg)
        if not valid_path(folder_path):
            print(f"Invalid path provided: {folder_path}. Please select a valid folder.")
            logging.error(f"Invalid path provided: {folder_path}. Please select a valid folder.")
            path_arg = None  # Reset path_arg to trigger folder selection dialog

    if not path_arg:
        # Get the user's desktop path
        desktop_path: str = os.path.join(os.path.expanduser("~"), "Desktop")

        root = tk.Tk()
        root.withdraw()  # Hide the root window
        # Create a temporary hidden window to set attributes
        temp_root = tk.Toplevel(root)
        temp_root.withdraw()  # Hide the temporary root window
        # Make the folder dialog appear on top
        temp_root.attributes('-topmost', True)
        folder_path: str = filedialog.askdirectory(
            parent=temp_root, title=windows_title, initialdir=desktop_path
        )
        temp_root.attributes('-topmost', False)
        temp_root.destroy()  # Destroy the temporary root

        if not folder_path:
            raise ValueError("Folder selection was cancelled. Please select a folder.")
        folder_path = os.path.normpath(folder_path)
        print_log(f"User select save folder path is: {folder_path}", logging.INFO)

    return folder_path


def is_valid_ip(ip: str) -> bool:
    """
    Validate the IP address format.

    Args:
        ip (str): The IP address to validate.

    Returns:
        bool: True if the IP address is valid, False otherwise.
    """
    pattern = re.compile(r"^(?:[0-9]{1,3}\.){3}[0-9]{1,3}$")
    return bool(pattern.match(ip)) and all(0 <= int(num) <= 255 for num in ip.split('.'))


def get_ip() -> str:
    """
    Prompt the user to enter a valid IP address.

    Returns:
        str: A valid IP address.
    """
    while True:
        ip = input("Please enter SEL Relay IP to download waveform: ")
        if is_valid_ip(ip):
            return ip
        else:
            print("Invalid IP address format. Please enter a valid IP address.")


def logger_init(
    out_path: str = None, log_name: str = "SEL Waveform download.log", log_level: int = logging.INFO
) -> None:
    """
    Initialize a logger that writes log messages to a timestamped file.

    Args:
        out_path (str, optional): The directory where the log file will be saved.
                                  If None, the log file will be created in the current directory.
        log_name (str, optional): The base name for the log file.
                                  Default is "SEL Waveform download.log".
        log_level (int, optional): The logging level (e.g., logging.INFO, logging.DEBUG).
                                   Default is logging.INFO.

    Returns:
        None
    """
    # Format the current date and time to append to the log file name
    current_time: str = datetime.now().strftime("%Y%m%d_%H.%M.%S.%f")
    log_filename: str = f"{current_time}_{log_name}"
    log_path: str = os.path.join(out_path, log_filename) if out_path else log_filename
    os.makedirs(os.path.dirname(log_path), exist_ok=True)
    file_handler_args: Tuple = (log_path, "w", "utf-8")
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s %(levelname)s %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        handlers=[logging.FileHandler(*file_handler_args)],
    )


def error_logger_init(out_path: str = None, log_level: int = logging.DEBUG) -> None:
    """
    Initialize an error-specific logger that logs only error and higher severity messages.

    Args:
        out_path (str, optional): The directory where the log file will be saved.
                                  If None, the log file will be created in the current directory.
        log_level (int, optional): The logging level (e.g., logging.INFO, logging.DEBUG).
                                   Default is logging.DEBUG.

    Returns:
        None
    """
    # Format the current date and time to append to the log file name
    current_time: str = datetime.now().strftime("%Y%m%d_%H.%M.%S.%f")
    log_filename: str = f"{current_time}_SEL Waveform download.log"
    log_path: str = os.path.join(out_path, log_filename) if out_path else log_filename
    os.makedirs(os.path.dirname(log_path), exist_ok=True)

    # Remove all handlers associated with the root logger object
    for handler in logging.root.handlers[:]:
        logging.root.removeHandler(handler)

    logger = logging.getLogger()
    logger.setLevel(log_level)

    # Add the custom ErrorFileHandler
    error_file_handler = ErrorFileHandler(log_path)
    formatter = logging.Formatter(
        "%(asctime)s %(levelname)s %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
    )
    error_file_handler.setFormatter(formatter)
    logger.addHandler(error_file_handler)


class ErrorFileHandler(logging.Handler):
    """
    A custom logging handler that tracks and writes log messages to a file
    when an error (or higher severity) occurs.

    Attributes:
        filename (str): The name of the file where log messages are written.
        error_occurred (bool): A flag indicating whether an error has occurred.

    Methods:
        emit(record): Processes a log record and writes it to the file
                      if an error or higher severity has occurred.
    """

    def __init__(self, filename):
        """
        Initialize the ErrorFileHandler.

        Args:
            filename (str): The name of the file where log messages will be written.
        """
        super().__init__()
        self.filename = filename
        self.error_occurred = False

    def emit(self, record):
        """
        Write log messages to the file if an error or higher severity occurs.

        Args:
            record (logging.LogRecord): The log record to process.
        """
        if record.levelno >= logging.ERROR:
            self.error_occurred = True
        if self.error_occurred:
            with open(self.filename, 'a') as log_file:
                log_file.write(self.format(record) + '\n')


def get_or_create_sel_download_log_folder(folder_name: str = "SEL download log") -> str:
    """
    Get or create the provided folder path. If it includes subdirectories,
    only the top-level directory will be set as hidden.

    Args:
        folder_name (str): The folder name or path, e.g., "SEL download log\\UI log".

    Returns:
        str: The absolute path of the provided folder.
    """
    current_working_directory = os.getcwd()
    folder_path = os.path.join(current_working_directory, folder_name)

    # 分離輸入的最上層資料夾 (根目錄)
    top_level_folder = os.path.join(current_working_directory, folder_name.split(os.sep)[0])
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
    # 設置文件夾為隱藏屬性 (僅在 Windows 上有效)
    set_hidden_attribute(top_level_folder)

    return os.path.abspath(folder_path)


def set_hidden_attribute(folder_path: str) -> None:
    """
    Set the Windows hidden attribute for a folder.

    Args:
        folder_path (str): The absolute path of the folder to hide.
    """
    # 定義 Windows API 的隱藏屬性值
    FILE_ATTRIBUTE_HIDDEN = 0x02

    # 調用 Windows API 設置屬性
    ctypes.windll.kernel32.SetFileAttributesW(folder_path, FILE_ATTRIBUTE_HIDDEN)


class ErrorFileHandler(logging.Handler):
    def __init__(self, filename):
        super().__init__()
        self.filename = filename
        self.error_occurred = False

    def emit(self, record):
        if record.levelno >= logging.ERROR:
            self.error_occurred = True
        if self.error_occurred:
            with open(file=self.filename, mode='a', encoding='utf-8') as log_file:
                log_file.write(self.format(record) + '\n')


def expand_event_ids(event_id_str: str) -> list[str]:
    """
    Expand a comma-separated string of event IDs into a sorted list of strings.

    This function parses a string containing individual event IDs and ranges
    (e.g., "1,2,5-8,10") and returns a sorted list of unique event IDs as strings.
    If the input is invalid or contains characters that do not follow the expected format,
    the function returns an empty list.

    Args:
        event_id_str (str): A string of comma-separated event IDs and ranges.
                            Single numbers (e.g., "1") and ranges (e.g., "1-3") are accepted.

    Returns:
        list[str]: A sorted list of unique event IDs as strings, or an empty list if the input is invalid.

    Example:
        >>> expand_event_ids("1,2,5-8,10,15-18")
        ['1', '2', '5', '6', '7', '8', '10', '15', '16', '17', '18']

        >>> expand_event_ids("invalid-input")
        []
    """
    # Validate the input
    if not isinstance(event_id_str, str) or not re.match(r'^[\d,\- ]*$', event_id_str):
        return []

    expanded_ids: list = []
    for id_val in event_id_str.split(','):
        id_val: str = id_val.strip()
        if re.match(r'^\d+-\d+$', id_val):  # Match "start-end" format
            start, end = map(int, id_val.split('-'))
            if start <= end:  # Ensure valid range
                expanded_ids.extend(range(start, end + 1))
            else:
                expanded_ids.extend(range(end, start + 1))
        elif id_val.isdigit():  # Handle single numbers
            expanded_ids.append(int(id_val))

    # Convert to strings and return a sorted list of unique IDs
    return [str(id_) for id_ in sorted(set(expanded_ids))]


def parse_chi_response(
    chi_in: str, event_ids_arg: Optional[List[str]] = None
) -> List[Tuple[str, str, str, str]]:
    """
    Parse and print the CHI command response in a formatted table.

    Args:
        chi_in (str): The response from the CHI command.
        event_ids_arg (Optional[List[str]]): The event IDs provided as command-line arguments.

    Returns:
        List[Tuple[str, str, str, str]]: List of tuples containing the event ID, date,
                                         event date time, and event description if found.
    """
    logging.debug(f"CHI original Data:\n{chi_in}")
    # Split the response into lines
    lines = chi_in.splitlines()

    # Find the line with the header and the line with data
    header_index = None
    for i, line in enumerate(lines):
        if "NUM" in line:
            header_index: int = i
            break

    if header_index is None:
        logging.error("No valid CHI data found.")
        return []

    # Extract headers and data lines
    headers: List[str] = lines[header_index].split(",")
    headers = [header.strip().strip('"') for header in headers]  # Clean header names
    data_lines: List[str] = lines[header_index + 1 :]

    # Filter out invalid lines
    filtered_data_lines: list = []
    for data_line in data_lines:
        if data_line.strip() in ["", "=>"]:
            continue
        elif any(char in data_line for char in ["\x03"]):
            break
        filtered_data_lines.append(data_line)

    data = pd.DataFrame(
        [data_line.split(",") for data_line in filtered_data_lines], columns=headers
    )
    data: pd.DataFrame = data[
        ['REC_NUM', 'YEAR', 'MONTH', 'DAY', 'HOUR', 'MIN', 'SEC', 'MSEC', 'EVENT']
    ]

    # Create a temporary column for the display format
    data['Formatted_Time'] = (
        data['YEAR']
        + '/'
        + data['MONTH'].str.zfill(2)
        + '/'
        + data['DAY'].str.zfill(2)
        + ' '
        + data['HOUR'].str.zfill(2)
        + ':'
        + data['MIN'].str.zfill(2)
        + ':'
        + data['SEC'].str.zfill(2)
        + '.'
        + data['MSEC'].str.zfill(3)
    )

    # Print the table with the formatted time
    display_data: pd.DataFrame = data[['REC_NUM', 'Formatted_Time', 'EVENT']]
    print(f"{display_data.to_string(index=False)}\n")

    logging.debug(f"CHI DataFrame Data:\n{data}")

    valid_events = []
    if event_ids_arg:
        # Check if the provided event IDs exist in the data
        for event_id in event_ids_arg:
            selected_event: pd.DataFrame = data[data['REC_NUM'] == event_id]
            if not selected_event.empty:
                selected_event = selected_event.iloc[0]
                event_date_time: str = (
                    f"{selected_event['YEAR']}.{selected_event['MONTH']:0>2}."
                    f"{selected_event['DAY']:0>2}"
                    f"-{selected_event['HOUR']:0>2}.{selected_event['MIN']:0>2}."
                    f"{selected_event['SEC']:0>2}.{selected_event['MSEC']:0>3}"
                )
                print(
                    f"Using provided Event Id Number: {selected_event['REC_NUM']}, "
                    f"Date: {selected_event['MONTH']:0>2}/{selected_event['DAY']:0>2}/"
                    f"{selected_event['YEAR']}"
                )
                valid_events.append(
                    (
                        selected_event['REC_NUM'],
                        f"{selected_event['MONTH']:0>2}/{selected_event['DAY']:0>2}"
                        f"/{selected_event['YEAR']}",
                        event_date_time,
                        selected_event['EVENT'],
                    )
                )

    # User input for selecting an event if no valid event IDs are provided
    if not valid_events:
        while True:
            try:
                selected_ids: str = input(
                    "Enter the Id Numbers of the events you want to download \n"
                    "(use ',' to separate events and '-' to specify a range, e.g., '1,2,5-8,10')\n"
                    "Type 'exit' to cancel: "
                ).strip()

                # Detect 'exit' input and raise cancellation signal
                if selected_ids.lower() == "exit":
                    raise CancelSignal("User chose to cancel the operation.")

                # Ensure input is not empty
                if not selected_ids:
                    raise ValueError("Input cannot be empty. Please enter valid Id Numbers.")

                selected_ids_list: list[int] = expand_event_ids(selected_ids)

                if not all(any(data['REC_NUM'] == id_) for id_ in selected_ids_list):
                    raise ValueError(
                        "One or more Id Numbers are not in the list. Please enter valid Id Numbers."
                    )
                break
            except ValueError as e:
                print(e)
        for selected_id in selected_ids_list:
            selected_event = data[data['REC_NUM'] == selected_id]
            if not selected_event.empty:
                selected_event = selected_event.iloc[0]
                event_date_time: str = (
                    f"{selected_event['YEAR']}.{selected_event['MONTH']:0>2}."
                    f"{selected_event['DAY']:0>2}"
                    f"-{selected_event['HOUR']:0>2}.{selected_event['MIN']:0>2}."
                    f"{selected_event['SEC']:0>2}.{selected_event['MSEC']:0>3}"
                )
                logging.debug(
                    f"Selected Event Id Number: {selected_event['REC_NUM']}, "
                    f"Date: {selected_event['MONTH']:0>2}/{selected_event['DAY']:0>2}/{selected_event['YEAR']}"
                )
                print(
                    f"Selected Event Id Number: {selected_event['REC_NUM']}, "
                    f"Date: {selected_event['MONTH']:0>2}/{selected_event['DAY']:0>2}/{selected_event['YEAR']}"
                )
                valid_events.append(
                    (
                        selected_event['REC_NUM'],
                        f"{selected_event['MONTH']:0>2}/{selected_event['DAY']:0>2}"
                        f"/{selected_event['YEAR']}",
                        event_date_time,
                        selected_event['EVENT'],
                    )
                )

    return valid_events


def clean_filename(filename: str, replacement: str = '') -> str:
    """
    Clean the filename by removing or replacing illegal characters.

    Args:
        filename (str): The original filename.
        replacement (str): The character to replace illegal characters with. Default is '' (remove illegal characters).

    Returns:
        str: The cleaned filename.
    """
    # Define a regex pattern to match illegal characters
    illegal_chars = r'[\/:*?"<>|]'
    # Replace illegal characters with the specified replacement character
    cleaned_filename = re.sub(illegal_chars, replacement, filename)
    return cleaned_filename


def get_previous_day(date_str: str) -> str:
    """
    Get the previous day for a given date string in 'MM/DD/YYYY' format.

    Args:
        date_str (str): The input date string in 'MM/DD/YYYY' format.

    Returns:
        str: The previous day's date in 'MM/DD/YYYY' format.
    """
    # Parse the input date string
    date: datetime = datetime.strptime(date_str, '%m/%d/%Y')
    # Subtract one day
    previous_day: datetime = date - timedelta(days=1)
    # Format the result back to 'MM/DD/YYYY' string format
    return previous_day.strftime('%m/%d/%Y')


def print_log(message: str, log_level: int = logging.DEBUG) -> None:
    """
    Print a message to the console and log it at the specified logging level.

    Args:
        message (str): The message to be printed and logged.
        log_level (int): The logging level to use. Default is logging.DEBUG.

    Returns:
        None
    """
    print(message)
    logging.log(level=log_level, msg=message)


class TelnetClient:
    """
    A simple Telnet client using telnetlib3 to connect to a device, send a command,
    and print the response.
    """

    def __init__(self, ip: str, port: int, encoding: str = 'utf-8') -> None:
        """
        Initialize the Telnet client with the IP address, port, and encoding.

        Args:
            ip (str): The IP address of the device.
            port (int): The port number to connect to.
            encoding (str): The character encoding to use.
        """
        self.ip: str = ip
        self.port: int = port
        self.encoding: str = encoding
        self.reader = None
        self.writer = None

    async def __aenter__(self) -> "TelnetClient":
        """
        Enter the asynchronous context manager.
        """
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc_value, exc_tb):
        """
        Exit the asynchronous context manager.
        """
        try:
            await self.close()
        except Exception as e:
            print(f"When close telnet to SEL Relay, error occurred: {e}")
            logging.error(f"When close telnet to SEL Relay, error occurred: {e}")

    async def connect(self) -> None:
        """
        Establish a Telnet connection to the device.
        """
        if not self.writer:
            try:
                self.reader, self.writer = await telnetlib3.open_connection(
                    host=self.ip,
                    port=self.port,
                    encoding=self.encoding,
                    connect_minwait=2,  # Minimum wait time for Telnet negotiations
                    connect_maxwait=3,  # Maximum wait time for Telnet negotiations
                )
                logging.info(f"Connected to {self.ip}:{self.port}")
            except Exception as e:
                logging.warn(f"Failed to connect: {e}")
                # Attempt to ping the device
                if await self.ping_device():
                    print(
                        f"Computer can ping to SEL Relay ({self.ip})."
                        "It might be in use by another user."
                    )
                else:
                    print(f"Unable to reach the device({self.ip}): {e}")
                raise

    async def close(self) -> None:
        """
        Close the Telnet connection.
        """
        print_log("SEL relay connect close call.", logging.INFO)
        if self.writer:
            try:
                if not self.writer.is_closing():
                    await self.send_command(command="QUI", show_res=True, timeout=1)
                    await self.send_command(command="EXIT", show_res=True, timeout=1)
                    print_log("!!!SEL Relay connection closed.!!!", logging.INFO)
                    self.writer.close()
                    await asyncio.sleep(0.5)  # Allow some time for the connection to close properly
                else:
                    print_log("Writer is already closing.", logging.WARN)
            except Exception as e:
                logging.error(f"Error closing connection: {e}")
                raise
        else:
            logging.warning("Connection was not established.")
            raise ConnectionError("SEL Relay no connect.")

    async def cancel_all_tasks(self):
        """
        Cancel all running asyncio tasks except the current one.
        """
        current_task = asyncio.current_task()
        for task in asyncio.all_tasks():
            if task is not current_task:
                task.cancel()
        await asyncio.gather(*asyncio.all_tasks(), return_exceptions=True)

    async def ping_device(self) -> bool:
        """
        Ping the device to check if it is reachable.

        Returns:
            bool: True if the device responds to ping, False otherwise.
        """
        try:
            # Use the ping command with 1 packet (Windows)
            process = await asyncio.create_subprocess_shell(
                f'ping -n 1 {self.ip}',
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            stdout: bytes
            stderr: bytes
            stdout, stderr = await process.communicate()

            if process.returncode == 0:
                logging.info(f"Ping to {self.ip} successful.")
                return True
            else:
                error_mes: str = f"Ping to {self.ip} failed: {stderr.decode().strip()}"
                print(error_mes)
                logging.warn(error_mes)
                return False
        except Exception as e:
            print(f"Error during ping: {e}")
            logging.error(f"Error during ping: {e}")
            return False

    async def send_command(self, command: str, show_res: bool = True, timeout: int = 10) -> str:
        """
        Send a command to the connected device and receive the response.

        Args:
            command (str): The command to send to the device.
            show_res (bool): If True, prints a message indicating the command was sent. Default is True.
            timeout (int): The maximum time in seconds to wait for a response. Default is 10 seconds.

        Raises:
            ConnectionError: If there is no active connection to any device.
            asyncio.TimeoutError: If the response is not received within the timeout period.
            ProhibitedCommandError: If the command is prohibited.

        Returns:
            str: The response from the device.
        """

        prohibited_commands: List[str] = ["SER C", "HIS C", "COM C", "2AC"]

        # Check for prohibited commands
        for prohibited_command in prohibited_commands:
            if prohibited_command.lower() in command.lower():
                raise ProhibitedCommandError(
                    command, f"The command '{prohibited_command}' is not allowed."
                )

        if not self.writer:
            raise ConnectionError("Not connected to SEL Relay.")

        # Wait until the device stops sending data
        if command.strip().lower() not in ["exit", "qui"]:
            logging.debug(f"Comaand is [{command}]. Start wait for previous data.")
            await self._wait_for_previous_data(10)
            logging.debug(f"Comaand is [{command}]. End waite for previous data.")

        command_print: str = (
            f"\nSend 【{command}】 command to Relay Device, please wait Relay feedback."
        )
        logging.debug(command_print)
        if show_res is True:
            print(command_print)
        command = command + '\r\n'
        try:
            self.writer.write(command)
            await self.writer.drain()
        except AttributeError as e:
            print_log(
                f"Failed to send command due to writer being None or closing: {e}", logging.WARN
            )
            raise ConnectionError("Writer is closing or already closed.")

        response: str = ""
        start_time = time.time()
        etx: bool = False

        spinner_task = asyncio.create_task(self.spinner())

        try:
            while True:
                if command.strip().lower() in ["exit", "qui"]:
                    await asyncio.sleep(1)
                    break
                chunk: str = await asyncio.wait_for(self.reader.read(1024), timeout)
                if chunk:
                    # Replace multiple line breaks with a single line break
                    chunk = re.sub(r'\r\n+', '\n', chunk)
                    response += chunk
                    if "\x03" in chunk:
                        etx = True
                        logging.debug("Read response to etx.")
                    if "=>" in chunk or "Password:" in chunk:
                        break
                    if etx and "=" in chunk:
                        logging.debug("Read response have etx and '=', break.")
                        break
                    start_time: float = time.time()  # Reset the timer on receiving valid data
                else:
                    if time.time() - start_time > timeout:
                        raise asyncio.TimeoutError
        except asyncio.TimeoutError:
            error_message: str = f"Timeout waiting for response to command: {command.strip()}"
            logging.error(error_message)
            raise ConnectionError(error_message)
        finally:
            spinner_task.cancel()

        response = re.sub(r'\r\n+', '\r\n', response)
        logging.info(f"Command sent: {command}")
        logging.info(f"Response received: {response}")
        return response

    async def _wait_for_previous_data(self, timeout: int = 10) -> None:
        """
        Wait for the device to finish sending any previous data.

        Args:
            timeout (int): The maximum time in seconds to wait for previous data to be fully received.

        Raises:
            asyncio.TimeoutError: If the data is not completely received within the timeout period.
        """
        start_time = time.time()
        while True:
            try:
                chunk = await asyncio.wait_for(self.reader.read(1024), timeout=1)
                logging.debug(f"Wait for previous data:{chunk}")
                if not chunk:
                    logging.debug(f"wait for previous data, chunk is empty: {chunk}")
                    await asyncio.sleep(0.5)
                    break  # No more data
                if time.time() - start_time > timeout:
                    raise asyncio.TimeoutError("Timeout waiting for previous data to be received.")
            except asyncio.TimeoutError:
                break  # No data received in the last interval, consider it done
            except Exception as e:
                print_log(
                    message=f"When wait for previous data, occur error: {e}",
                    log_level=logging.ERROR,
                )
                # logging.error(f"When wait for previous data, occur error: {e}")
                break

    async def spinner(self):
        spinner_chars: List[str] = ['|', '/', '-', '\\']
        idx = 0
        while True:
            idx: int = (idx + 1) % len(spinner_chars)
            await aprint(spinner_chars[idx], end='\r', flush=True)
            await asyncio.sleep(0.1)

    async def get_relay_name(self) -> str | None:
        """
        Retrieve the relay name from the SEL device using the "id" command.

        The function sends the "id" command to the SEL device and extracts the relay name from
        the "DEVID" field in the response.
        If the "DEVID" field is not found in the response, the function returns None.

        Returns:
            str | None: The relay name if found in the "DEVID" field, otherwise None.
        """
        id_response: str = await self.send_command(command="id", show_res=False)
        if "DEVID" in id_response:
            # Extract DEVID value
            for line in id_response.splitlines():
                if "DEVID" in line:
                    return line.split("=")[1].split(",")[0].strip('"')
        else:
            return None

    async def get_fid(self, retries: int = 1) -> str | None:
        """
        Retrieve the Firmware Identification (FID) from the SEL device using the "id" command.

        The function attempts to send the "id" command to the SEL device and extracts the FID
        from the response. It retries up to the specified number of times if the command fails
        due to connection issues or if the FID is not found in the response.

        Args:
            retries (int): The maximum number of attempts to retrieve the FID.

        Returns:
            str | None: The FID value if found in the response, otherwise None.

        Raises:
            ConnectionError: If the connection to the device fails after all retries.
            asyncio.TimeoutError: If the response is not received within the timeout.
            Exception: If any unexpected error occurs during execution.
        """
        for attempt in range(1, retries + 1):  # Retry up to `retries` times
            try:
                id_response: str = await self.send_command(command="id", show_res=False)
                logging.debug(f"ID command response: {id_response}")

                if not id_response:  # Handle empty or invalid response
                    logging.error(f"Empty response received on attempt {attempt}.")
                    if attempt == retries:
                        return None
                    await asyncio.sleep(3)  # Wait before retrying
                    continue

                if "FID" in id_response:
                    # Extract FID value
                    for line in id_response.splitlines():
                        logging.debug(f"Processing line: {line}")
                        if "FID" in line:
                            return line.split("=")[1].split(",")[0].strip('"')

                logging.error("FID not found in the response.")
                if attempt < retries:
                    await asyncio.sleep(3)  # Wait before retrying

            except (ConnectionError, asyncio.TimeoutError) as e:
                logging.warning(f"Attempt {attempt} failed: {e}")
                if attempt == retries:  # If max retries reached, raise the exception
                    raise e
            except Exception as e:
                logging.error(f"Unexpected error occurred: {e}")
                raise e

        return None

    async def download_waveform(
        self, event_id: str, cyles: str, samples: str, model: str = "other"
    ) -> Coroutine[Any, Any, Tuple[str, str | None, str]]:
        """
        Download waveform data for the given event ID, event length (cyles), and samples per cycle.

        Args:
            event_id (str): The event ID for which to download the waveform.
            cyles (str): The length of the event in cycles.
            samples (str): The number of samples per cycle (4 or all).

        Returns:
            str: The response from the device after successfully downloading the waveform.
            str: The length of the event in cycles.
            str: The cev command.
        """
        cev_response: str = None
        cev_command: str = None
        timeout: int = 60
        try:
            match model:
                case "311L_351":
                    while True:
                        # Construct the CEV command based on samples per cycle
                        if samples == "4":
                            cev_command: str = f"CEV L{cyles} {event_id}"
                        elif samples.lower() == 'all':
                            cev_command = f"CEV R L{cyles} {event_id}"
                        else:
                            print(
                                "Samples/Cyles can only enter 4 or all. Now download 4 Samples/Cyles"
                            )
                            cev_command = f"CEV L{cyles} {event_id}"

                        cev_response: str = await self.send_command(
                            command=cev_command, timeout=timeout
                        )

                        if "No Data Available" in cev_response:
                            print(
                                "No Data Available. The entered Event Length is too long. "
                                "Please re-enter."
                            )
                            cyles = input("Please enter Event Length(Cyles) to download: ")
                        else:
                            print("Download waveform completed")
                            break

                case "487E":
                    while True:
                        if samples == "4":
                            cev_command: str = f"CEV {event_id}"
                        elif samples == 'all':
                            cev_command = f"CEV {event_id} S8"
                        else:
                            print(
                                "Samples/Cyles can only enter 4 or all. Now download 4 Samples/Cyles"
                            )
                            cev_command = f"CEV {event_id}"
                        cev_response: str = await self.send_command(
                            command=cev_command, timeout=timeout
                        )
                        if "No Data Available" in cev_response:
                            print_log(
                                message=f"No Data can download. Command: {cev_command}",
                                log_level=logging.ERROR,
                            )
                            break
                        print("Download waveform completed")
                        break

                case "487B":
                    while True:
                        if samples == "4":
                            cev_command: str = f"CEV {event_id}"
                        elif samples == 'all':
                            cev_command = f"CEV R {event_id}"
                        else:
                            print(
                                "Samples/Cyles can only enter 4 or all. Now download 4 Samples/Cyles"
                            )
                            cev_command = f"CEV {event_id}"
                        cev_response: str = await self.send_command(
                            command=cev_command, timeout=timeout
                        )
                        if "No Data Available" in cev_response:
                            print_log(
                                message=f"No Data can download. Command: {cev_command}",
                                log_level=logging.ERROR,
                            )
                            break
                        print("Download waveform completed")
                        break

                case "other":
                    print_log(
                        message="This model of relay accident waveform download is not supported. "
                        "Only download 4 samples/cyles accident waveforms.",
                        log_level=logging.WARN,
                    )
                    cev_command: str = f"CEV {event_id}"
                    cev_response: str = await self.send_command(
                        command=cev_command, timeout=timeout
                    )
                    if "No Data Available" in cev_response:
                        print_log(
                            message=f"No Data can download. Command: {cev_command}",
                            log_level=logging.ERROR,
                        )
        except ConnectionError as e:
            print_log(f"Connect Error occurred (CEV command: {cev_command}): {e}", logging.WARN)
        except Exception as e:
            print_log(f"An Error occured (CEV command: {cev_command}): {e}", logging.ERROR)

        finally:
            return cev_response, cyles, cev_command


def is_positive_integer(input_str: Any) -> bool:
    """
    Checks if the input represents a positive integer.

    Args:
        input_str (any): The input to check. Can be of any type.

    Returns:
        bool: True if the input is a positive integer in string format,
              False otherwise.
    """
    if not isinstance(input_str, str):
        return False
    return input_str.isdigit() and int(input_str) > 0


def create_cancel_file(save_path: str, his_ser_responses: list) -> None:
    """
    Writes a cancellation message and historical responses to a file.

    This function creates or overwrites a file named `his+ser_cancel.txt`
    in the specified save path. The file will contain the list of historical
    responses followed by a cancellation message. If an error occurs during
    file writing, it logs the error.

    Args:
        save_path (str): The directory path where the cancellation file will
                         be saved.
        his_ser_responses (list): A list of strings containing historical
                                  responses to be written into the file.

    Returns:
        None

    Raises:
        This function does not raise exceptions directly but logs any
        errors encountered during file writing.
    """
    try:
        his_ser_path_file: str = os.path.join(save_path, f"his+ser_cancel.txt")
        with open(his_ser_path_file, "w", encoding="utf-8") as file:
            file.write("\n".join(his_ser_responses))
            file.write("\n!!!User cancel download.!!!")
    except Exception as e:
        print_log(f"Failed to write to cancel file: {e}", logging.ERROR)


class ProhibitedCommandError(Exception):
    def __init__(self, command: str, message="This command is not allowed") -> None:
        self.command: str = command
        self.message: str = message
        super().__init__(self.message)

    def __str__(self) -> str:
        return f"{self.command} - {self.message}"


class CancelSignal(Exception):
    def __init__(self, message="Operation was cancelled by the user.") -> None:
        self.message: str = message
        super().__init__(self.message)

    def __str__(self) -> str:
        return f"{self.message}"
