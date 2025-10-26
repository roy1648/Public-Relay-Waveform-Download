#!/usr/bin/env python
# coding=utf-8
'''
File Description:
Author          : CHEN, JIA-LONG
Create Date     : 2024-06-14 14:50
FilePath        : \\SEL relay download core.py
Copyright © 2024 CHEN JIA-LONG.
'''
import argparse
import asyncio
import logging
import os
from datetime import datetime
from typing import List, Tuple

import win32api
import win32con

import module as mod

client = None


async def async_close_client() -> None:
    """
    Asynchronously force closes the SEL Relay connection.

    If the client is connected, logs the force close operation and attempts to close the connection.
    Logs any errors encountered during the force close attempt.

    Returns:
        None
    """
    if client is not None:
        mod.print_log("Force Closing SEL Relay connection...", logging.INFO)
        try:
            await client.close()
        except Exception as e:
            logging.error(f"Force close sel relay have error: {e}")
        mod.print_log("Force Closed SEL Relay connection.", logging.INFO)


def on_exit(event) -> bool:
    """
    Handles various console events by performing necessary cleanup operations and logging the event.

    Args:
        event: The event that triggered this handler.

    Returns:
        bool: True if the event was handled, False otherwise.
    """
    if event in [
        win32con.CTRL_C_EVENT,
        win32con.CTRL_BREAK_EVENT,
        win32con.CTRL_CLOSE_EVENT,
        win32con.CTRL_LOGOFF_EVENT,
        win32con.CTRL_SHUTDOWN_EVENT,
    ]:
        event_map: dict[int, str] = {
            win32con.CTRL_C_EVENT: "CTRL_C_EVENT",
            win32con.CTRL_BREAK_EVENT: "CTRL_BREAK_EVENT",
            win32con.CTRL_CLOSE_EVENT: "CTRL_CLOSE_EVENT",
            win32con.CTRL_LOGOFF_EVENT: "CTRL_LOGOFF_EVENT",
            win32con.CTRL_SHUTDOWN_EVENT: "CTRL_SHUTDOWN_EVENT",
        }
        mod.print_log(
            f"Console event {event_map[event]} occurred. Performing cleanup...", logging.INFO
        )
        if client is not None:
            try:
                loop: asyncio.AbstractEventLoop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                loop.run_until_complete(async_close_client())
                loop.close()
            except Exception as e:
                mod.print_log(f"Force close sel relay have error: {e}", logging.ERROR)
        else:
            logging.error("Client is None. No Sel relay connect.")
        return True  # 返回True告訴系統我們已經處理了這個事件
    return False


async def main() -> None:
    """
    Main function to create a Telnet client, send a command, and print the response.
    """
    global client  # 宣告全域變數
    try:
        # Define valid log levels
        LOG_LEVELS: dict[str, int] = {
            'DEBUG': logging.DEBUG,
            'INFO': logging.INFO,
            'WARNING': logging.WARNING,
            'ERROR': logging.ERROR,
            'CRITICAL': logging.CRITICAL,
        }
        parser = argparse.ArgumentParser(description="Download event data from SEL Relay.")
        parser.add_argument('-c', '--cyles', type=int, help='Event Length (Cyles) to download')
        parser.add_argument(
            '-s',
            '--samples',
            type=str,
            choices=['4', 'all', 'ALL'],
            help='Samples/Cyles to download (4 or all)',
        )
        parser.add_argument('-i', '--ip', type=str, help='Enter SEL Relay IP')
        parser.add_argument(
            '-p', '--port', type=int, default=23, help='Enter SEL Relay IP port, default is 23'
        )
        parser.add_argument('-d', '--dir', type=str, help='Directory to save waveform files')
        parser.add_argument(
            '-eid',
            '--event_id',
            type=str,
            help="Comma-separated Event IDs to download. Use ',' to separate events "
            "and '-' to specify a range (e.g., '1,2,5-8,10').",
        )  # Allow multiple event IDs

        args: argparse.Namespace
        unknown: list[str]
        args, unknown = parser.parse_known_args()

        # Display provided arguments
        if args.ip is not None:
            print(f"SEL Relay IP: {args.ip}")
        if args.port != 23:
            print(f"SEL Relay IP port: {args.port}")
        if args.cyles is not None:
            print(f"Download Event Length (Cyles): {args.cyles}")
        if args.samples is not None:
            print(f"Download Samples/Cyles (4 or all): {args.samples}")
        if args.event_id is not None:
            print(f"Comma-separated Event IDs to download: {args.event_id}")
        if args.dir is not None:
            print(f"Directory to save waveform files: {args.dir}")

        # Process the log level argument separately
        log_level = None
        for i, arg in enumerate(unknown):
            if arg in ['-log', '--log'] and i + 1 < len(unknown):
                log_level_str: str = unknown[i + 1].upper()
                if log_level_str in LOG_LEVELS:
                    log_level: int = LOG_LEVELS[log_level_str]
                    break
        log_folder: str = mod.get_or_create_sel_download_log_folder()
        if log_level is not None:
            mod.logger_init(out_path=log_folder, log_level=log_level)
            logging.info("Log file created, start record main process.")
            print(f"Log enable: {log_level_str}")
        else:
            mod.error_logger_init(out_path=log_folder)

        # Validate the IP address
        ip: str = args.ip if args.ip and mod.is_valid_ip(args.ip) else mod.get_ip()

        encoding = "utf-8"  # Replace with the character encoding used by PuTTY

        select_folder: str = "Please select the folder where you want to store the waveform file."
        save_path: str = mod.select_folder(windows_title=f"{select_folder}", path_arg=args.dir)

        async with mod.TelnetClient(ip=ip, port=args.port, encoding=encoding) as client:
            his_ser_responses: list = []
            fid: str = None
            fid: str | None = await client.get_fid(retries=5)
            mod.print_log(message=f"FID= {fid}", log_level=logging.INFO)

            model: str = "other"
            if "311L" in fid or "351" in fid or "311C" in fid:
                model = "311L_351"
            elif "487E" in fid:
                model = "487E"
            elif "487B" in fid:
                model = "487B"
            else:
                model = "other"
            logging.debug(f"Model variable = {model}")

            his_ser_responses.append(f"Connect IP: {ip}")
            # Get current time save in his+ser data.
            now: datetime = datetime.now()
            formatted_time: str = now.strftime("%Y/%m/%d %A %H:%M:%S.%f")

            his_ser_responses.append(f"Current computer time: {formatted_time}")
            his_ser_responses.append("==================================================\n")
            # Collect responses for HIS commands
            for command in ["ACC", "PASS", "HIS"]:
                try:
                    if not client.writer.is_closing():
                        response: str = await client.send_command(command)
                        print(f"Response from SEL Relay: {response}")
                        his_ser_responses.append(response)
                    else:
                        mod.print_log(
                            f"Writer is already closing. Command: {command}", logging.WARN
                        )
                except ConnectionError as e:
                    mod.print_log(f"Writer is already closing. Command: {command}", logging.WARN)
                except Exception as e:
                    logging.error(f"Error during {command} command: {e}")
                    continue  # Skip to the next command if an error occurs

            # Convert event_id argument to a list if provided
            event_ids: list[int] = mod.expand_event_ids(args.event_id if args.event_id else "")
            chi_response: str = await client.send_command("CHI")
            try:
                valid_events: List[Tuple[str]] = mod.parse_chi_response(
                    chi_in=chi_response, event_ids_arg=event_ids
                )
            except mod.CancelSignal as e:
                mod.print_log(e, logging.INFO)
                mod.create_cancel_file(save_path, his_ser_responses)
                return
            # Validate samples argument
            samples: str = args.samples.lower() if args.samples in ['4', 'all', 'ALL'] else '0'
            while samples != "4" and samples.lower() != "all":
                samples = input("Please enter Samples/Cyles (4 or all) to download: ")
                if samples != "4" and samples.lower() != "all":
                    print("Samples/Cyles can only enter 4 or all, please enter again.")
            logging.debug(f"samples：{samples}")

            # Validate cyles argument
            download_cyles: str = (
                str(args.cyles)
                if hasattr(args, 'cyles')
                and args.cyles is not None
                and mod.is_positive_integer(str(args.cyles))
                else ''
            )
            logging.debug(f"download cyles：{download_cyles}")
            if not download_cyles:
                while True:
                    try:
                        download_cyles = input(
                            "Please enter Event Length (Cyles) to download (or 'exit' to exit): "
                        ).strip()
                        if download_cyles.lower() == "exit":
                            print("!!!User cancel download.!!!")
                            mod.create_cancel_file(save_path, his_ser_responses)
                            return
                        elif mod.is_positive_integer(download_cyles):
                            print(f"Valid Event Length (Cyles) entered: {download_cyles}")
                            break
                        else:
                            download_cyles = ''
                            print("Invalid input. Please enter a positive integer.")
                    except Exception as e:
                        # 捕捉其他例外，避免無限迴圈
                        mod.print_log(f"An error occurred: {e}. Exiting.", logging.ERROR)
                        return

            # Get SEL Relay Name
            device_id: str | None = await client.get_relay_name()

            # Download SER data.
            downloaded_date: list = []
            ser_records: list = []
            logging.debug(f"vaild_events variable: \n{valid_events}\n")
            for event_id, date, event_date_time, trip_event in valid_events:
                if date not in downloaded_date:
                    ser_response: str = await client.send_command(
                        f"SER {mod.get_previous_day(date_str=date)} {date}"
                    )
                    print(f"Response from SEL Relay: {ser_response}")
                    his_ser_responses.append(ser_response)
                    ser_records.append(ser_response)
                    downloaded_date.append(date)

            # Check for None, case-insensitive "invalid", or "No SER Data"
            if any(
                response is None
                or any(substring in response.lower() for substring in ["invalid", "no ser data"])
                for response in ser_records
            ):
                ser_response: str = await client.send_command("SER 50")
                print(f"Response from SEL Relay: {ser_response}")
                his_ser_responses.append(ser_response)

            # Set and create his+ser filename
            if device_id:
                his_ser_filename: str = f"his+ser_{device_id}_{event_date_time}"
            else:
                his_ser_filename: str = f"his+ser_{event_date_time}"
            his_ser_filename = mod.clean_filename(his_ser_filename)  # Clean the filename

            his_ser_path_file: str = os.path.join(save_path, f"{his_ser_filename}.txt")
            logging.debug(f"Save his+ser path+filename:{his_ser_path_file}")
            logging.debug(f"his+ser file content:\n{his_ser_responses}")
            with open(his_ser_path_file, "w", encoding="utf-8") as file:
                file.write("\n".join(his_ser_responses))

            logging.debug(f"vaild_events variable: \n{valid_events}\n")
            for event_id, date, event_date_time, trip_event in valid_events:
                cev_response: str = None
                cev_command: str = None

                # Download waveform
                logging.debug(f"In for round, event_id variable: {event_id}")
                cev_response, download_cyles, cev_command = await client.download_waveform(
                    event_id=event_id, cyles=download_cyles, samples=samples, model=model
                )

                # Set cev filename
                if device_id:
                    cev_filename = f"{device_id}_{event_date_time}_{trip_event}_{cev_command}"
                else:
                    cev_filename: str = f"{cev_command}_{trip_event}_{event_date_time}"
                cev_filename = mod.clean_filename(cev_filename)  # Clean the filename

                # Save cev file
                if cev_response is None:
                    with open(his_ser_path_file, "a", encoding="utf-8") as file:
                        file.write(f"\nFailed to download waveform file: {cev_filename}.cev")
                else:
                    cev_path_filename: str = os.path.join(save_path, f"{cev_filename}.cev")
                    logging.debug(f"CEV filename & path: {cev_path_filename}")
                    logging.debug(f"CEV content:\n{cev_response}")
                    with open(cev_path_filename, "w", encoding="utf-8") as file:
                        file.write(cev_response)

    except ConnectionError as e:
        mod.print_log(f"An connect error occurred: {e}", logging.WARN)

    except Exception as e:
        print(f"An error occurred: {e}")
        logging.error(f"An error occurred: {e}")


if __name__ == "__main__":
    try:
        win32api.SetConsoleCtrlHandler(on_exit, True)
        asyncio.run(main())
    except Exception as e:
        print(f"An error occurred: {e}")
        logging.error(f"An error occurred: {e}")
    print("Wishing you all the best in your work.")
    input("All programs have been completed, please enter any key to end.")
