#!/usr/bin/env python
# coding=utf-8
'''
File Description:
Author          : CHEN, JIA-LONG
Create Date     : 2024-11-19 13:44
FilePath        : \\SEL relay download.py
Copyright © 2024 CHEN JIA-LONG.
'''

import datetime
import gettext
import logging
import os
import platform
import re
import subprocess
import sys

import wx

import module as mod
import Sel_GUI

_ = gettext.gettext


# ---------------------------------------------------------------------------

# This is how you pre-establish a file filter so that the dialog
# only shows the extension(s) you want it to.
wildcard = "SEL Download exe (*.exe)|*.exe"

# ---------------------------------------------------------------------------


class GUIFrame(Sel_GUI.SEL_Download):
    def __init__(self, parent) -> None:
        Sel_GUI.SEL_Download.__init__(self, parent)

        # Icon set
        icon_path = resource_path("download_ui_icon.ico")
        self.SetIcon(wx.Icon(icon_path, wx.BITMAP_TYPE_ICO))

        # Debug setting
        self.DEBUG_PASSWORD = "880330"
        self.savepath: str | None = None
        self.exefile: str = os.path.join(os.getcwd(), "SEL relay download core.exe")
        self.m_staticEXEFile.SetLabelText(self.exefile)
        self.m_staticEXEFile.Wrap(self.GetSize()[0] - 30)

        # 初始化 Debug 模式
        self.debug_mode: bool = False
        # 設置快捷鍵組合 (Ctrl + Shift + Alt + D)
        accel_tbl = wx.AcceleratorTable(
            [(wx.ACCEL_CTRL | wx.ACCEL_SHIFT | wx.ACCEL_ALT, ord('D'), wx.ID_HIGHEST + 1)]
        )
        self.SetAcceleratorTable(accel_tbl)

        # 綁定快捷鍵事件
        self.Bind(wx.EVT_MENU, self.on_debug_shortcut, id=wx.ID_HIGHEST + 1)

    def on_debug_shortcut(self, event):
        """快捷鍵事件處理，啟用或停用 Debug 模式"""
        # 顯示密碼輸入對話框
        password_dialog = PasswordDialog(self, title="輸入除錯密碼: 生日快樂")
        if password_dialog.ShowModal() == wx.ID_OK:
            input_password = password_dialog.input_password

            if input_password == self.DEBUG_PASSWORD:
                self.debug_mode = True
                log_folder = mod.get_or_create_sel_download_log_folder("SEL download log\\UI log")
                mod.logger_init(out_path=log_folder, log_level=logging.DEBUG)
                logging.info("Log file created, start record UI main process.")
                wx.MessageBox("Debug 模式已啟用！", "訊息", wx.OK | wx.ICON_INFORMATION)
            else:
                wx.MessageBox("密碼錯誤，無法啟用 Debug 模式。", "錯誤", wx.OK | wx.ICON_ERROR)
        password_dialog.Destroy()

        event.Skip()

    def on_resize(self, event) -> None:
        self.m_staticEXEFile.SetLabelText(self.exefile)
        self.m_staticEXEFile.Wrap(self.GetSize()[0] - 30)
        event.Skip()

    def OnFloderClick(self, event) -> None:
        # In this case we include a "New directory" button.
        default_path = (
            self.savepath if self.savepath else os.path.join(os.path.expanduser("~"), "Desktop")
        )
        dlg = wx.DirDialog(
            self,
            _(u"選擇存檔路徑"),
            defaultPath=default_path,
            style=0,
            # | wx.DD_DIR_MUST_EXIST
            # | wx.DD_CHANGE_DIR
        )

        # If the user selects OK, then we process the dialog's data.
        # This is done by getting the path data from the dialog - BEFORE
        # we destroy it.
        if dlg.ShowModal() == wx.ID_OK:
            self.savepath = dlg.GetPath()
            self.m_textCtrlFloder.SetValue(f"{self.savepath}")

        # Only destroy a dialog after you're done with it.
        dlg.Destroy()
        event.Skip()

    def OnKillFocus_FloderText(self, event):
        """檢查輸入框中的值是否為合法目錄"""
        input_path: str = self.m_textCtrlFloder.GetValue().strip()
        invalid_chars_pattern = r'[*?"<>|]'
        if input_path and re.search(invalid_chars_pattern, input_path):
            wx.MessageBox(
                f"輸入的路徑無效 ({input_path})，請重新輸入。", "警告", wx.OK | wx.ICON_WARNING
            )
            # 避免 NoneType 問題，將 self.savepath 設為空字串或有效路徑
            safe_savepath: str = self.savepath if self.savepath else ""
            self.m_textCtrlFloder.SetValue(safe_savepath)
        # 檢查是否為絕對路徑
        elif input_path and not os.path.isabs(input_path):
            wx.MessageBox(
                f"輸入的路徑不是絕對路徑 ({input_path})，請重新輸入。",
                "警告",
                wx.OK | wx.ICON_WARNING,
            )
            # 恢復為安全值
            safe_savepath: str = self.savepath if self.savepath else ""
            self.m_textCtrlFloder.SetValue(safe_savepath)
        else:
            # 如果通過檢查，保存路徑
            self.savepath = input_path

        event.Skip()  # 確保焦點轉移不受影響

    def OnEXEFileClick(self, event):
        """
        Create the dialog. In this case the current directory is forced as the starting
        directory for the dialog, and no default file name is forced. This can easily
        be changed in your program. This is an 'open' dialog, and allows multitple
        file selections as well.

        Finally, if the directory is changed in the process of getting files, this
        dialog is set up to change the current working directory to the path chosen.
        """
        dlg = wx.FileDialog(
            self,
            message="選擇SEL Download執行檔位置",
            defaultDir=os.path.dirname(self.exefile),
            defaultFile="",
            wildcard=wildcard,
            style=wx.FD_OPEN | wx.FD_CHANGE_DIR | wx.FD_FILE_MUST_EXIST | wx.FD_PREVIEW,
        )

        # Show the dialog and retrieve the user response. If it is the OK response,
        # process the data.
        if dlg.ShowModal() == wx.ID_OK:
            # This returns a Python list of files that were selected.
            self.exefile = dlg.GetPath()
            self.m_staticEXEFile.SetLabelText(self.exefile)
            self.m_staticEXEFile.Wrap(self.GetSize()[0] - 30)

        # Destroy the dialog. Don't do this until you are done with it!
        # BAD things can happen otherwise!
        dlg.Destroy()
        event.Skip()

    def OnDownloadClick(self, event) -> None:
        ip: str = self.m_textCtrlDownIP.GetValue()
        port: str = self.m_textCtrlPort.GetValue()
        sample: str = self.m_choiceSample.GetStringSelection()
        cyles: str = self.m_textCtrlCyles.GetValue()
        eid: str = self.m_textCtrlEid.GetValue()
        args: list = [
            format_var("-i", ip),
            format_var("-p", port),
            format_var("-s", sample),
            format_var("-c", cyles),
            format_var("-eid", eid),
            format_var("-d", self.savepath),
        ]
        args = [arg for arg in args if arg]
        window_title: str = combine_cmd_name(ip, self.savepath)
        if self.debug_mode:
            args.append("-log DEBUG")
        # 檢查 .exe 檔案是否存在
        if not os.path.isfile(self.exefile):
            wx.MessageBox(
                f"無法找到執行檔案：\n{self.exefile}\n請檢查路徑是否正確。",
                "錯誤",
                wx.OK | wx.ICON_ERROR,
            )
            return  # 終止後續操作

        command: str = f'start "{window_title}" "{self.exefile}" {" ".join(args)}'
        if self.debug_mode:
            logging.debug(f"Command: {command}")

        try:
            # 啟動子進程
            execute_command(command)
            # subprocess.Popen(command, shell=True, creationflags=subprocess.DETACHED_PROCESS)
        except Exception as e:
            wx.MessageBox(f"執行檔案時發生錯誤：\n{e}", "錯誤", wx.OK | wx.ICON_ERROR)

        self.Raise()
        wx.CallLater(500, lambda: self.SetWindowStyle(self.GetWindowStyle() & ~wx.STAY_ON_TOP))
        event.Skip()

    def OnCancelClick(self, event):
        """處理取消按鈕的點擊事件，結束整個應用程序"""
        confirm = wx.MessageBox("確定要結束軟體嗎？", "結束確認", wx.YES_NO | wx.ICON_QUESTION)
        if confirm == wx.YES:
            if self.debug_mode:
                logging.shutdown()
            self.Destroy()
            wx.GetApp().ExitMainLoop()
            self.Close()  # 結束所有 wxWidgets 的事件循環


def execute_command(command: str) -> None:
    """
    Executes a given command while ensuring compatibility with Windows 7.

    Args:
        command (str): The command to execute.
    """
    # 檢查作業系統
    if platform.system() == "Windows":
        try:
            if platform.version().startswith("6.1"):  # Windows 7
                # Windows 7 使用 CREATE_NEW_CONSOLE
                subprocess.Popen(command, shell=True, creationflags=subprocess.CREATE_NEW_CONSOLE)
            else:
                # Windows 8+ 使用 DETACHED_PROCESS
                subprocess.Popen(command, shell=True, creationflags=subprocess.DETACHED_PROCESS)
        except Exception as e:
            logging.error(f"執行指令時發生錯誤: {e}")
    else:
        wx.MessageBox("此程式僅適用於 Windows 平台", "平台不支援", wx.OK | wx.ICON_WARNING)


def format_var(prefix: str, value: str) -> str:
    """
    Format a variable into a specific string format.

    This function checks if the variable is None or an empty string. If the
    variable has a value, it returns a formatted string with the prefix and
    value. Otherwise, it returns an empty string.

    Args:
        prefix (str): The prefix to prepend to the value (e.g., "-i").
        value (str): The variable to check and format.

    Returns:
        str: A formatted string like "prefix value" or an empty string if the
            variable is None or empty.
    """
    # Check if the value is None or an empty string after stripping whitespace
    if value is None or value.strip() == "":
        return ""
    value = value.strip()
    if " " in value:
        value = f'"{value}"'
    # Return the formatted string with the prefix and stripped value
    return f"{prefix} {value.strip()}"


def combine_cmd_name(ip: str, savepath: str) -> str:
    """
    組合兩個變數。如果任一變數為空，忽略該變數；兩個都為空時，使用當下時間作為變數。
    """
    # 檢查變數是否為空或 None
    if not ip and not savepath:
        # 兩個變數都為空時，使用當下時間
        return f'{datetime.datetime.now().strftime("%H:%M:%S")}_Start Download'

    # 組合變數，忽略為空的值
    components = [value for value in (ip, savepath) if value]  # 過濾掉空值
    return "_".join(components)  # 以底線組合非空值


def resource_path(relative_path):
    """獲取資源的絕對路徑，適用於 PyInstaller 打包後的情況"""
    if hasattr(sys, '_MEIPASS'):
        # PyInstaller 打包後的臨時目錄
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)


class PasswordDialog(wx.Dialog):
    def __init__(self, parent, title):
        super().__init__(parent, title=title, size=(300, 165))

        self.input_password = None

        # 建立佈局
        vbox = wx.BoxSizer(wx.VERTICAL)

        # 提示文字
        self.message = wx.StaticText(self, label="請輸入除錯密碼以啟用 Debug 模式：")
        vbox.Add(self.message, flag=wx.ALL | wx.EXPAND, border=10)

        # 密碼輸入框
        self.text_ctrl = wx.TextCtrl(self, style=wx.TE_PASSWORD)
        vbox.Add(self.text_ctrl, flag=wx.ALL | wx.EXPAND, border=10)

        # 按鈕區域
        hbox = wx.BoxSizer(wx.HORIZONTAL)
        self.ok_button = wx.Button(self, label="確定", id=wx.ID_OK)
        self.cancel_button = wx.Button(self, label="取消", id=wx.ID_CANCEL)
        hbox.Add(self.ok_button, flag=wx.RIGHT, border=5)
        hbox.Add(self.cancel_button)
        vbox.Add(hbox, flag=wx.ALIGN_CENTER | wx.ALL, border=10)

        self.SetSizer(vbox)

        # 綁定事件
        self.ok_button.Bind(wx.EVT_BUTTON, self.on_ok)
        self.cancel_button.Bind(wx.EVT_BUTTON, self.on_cancel)

    def on_ok(self, event):
        """處理確定按鈕事件"""
        self.input_password = self.text_ctrl.GetValue()
        self.EndModal(wx.ID_OK)

    def on_cancel(self, event):
        """處理取消按鈕事件"""
        self.EndModal(wx.ID_CANCEL)


if __name__ == '__main__':
    app = wx.App()
    frm = GUIFrame(None)
    frm.Show()
    app.MainLoop()
