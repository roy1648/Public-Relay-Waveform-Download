# -*- coding: utf-8 -*-

###########################################################################
## Python code generated with wxFormBuilder (version 4.2.1-0-g80c4cb6)
## http://www.wxformbuilder.org/
##
## PLEASE DO *NOT* EDIT THIS FILE!
###########################################################################

import gettext

import wx
import wx.xrc

_ = gettext.gettext

###########################################################################
## Class SEL_Download
###########################################################################


class SEL_Download(wx.Frame):

    def __init__(self, parent):
        wx.Frame.__init__(
            self,
            parent,
            id=wx.ID_ANY,
            title=_(u"下載SEL電驛事故"),
            pos=wx.DefaultPosition,
            size=wx.Size(700, 470),
            style=wx.DEFAULT_FRAME_STYLE | wx.ALWAYS_SHOW_SB | wx.FULL_REPAINT_ON_RESIZE,
        )

        self.SetSizeHints(wx.DefaultSize, wx.DefaultSize)
        self.SetFont(
            wx.Font(
                14,
                wx.FONTFAMILY_SWISS,
                wx.FONTSTYLE_NORMAL,
                wx.FONTWEIGHT_NORMAL,
                False,
                "微軟正黑體",
            )
        )
        self.SetForegroundColour(wx.SystemSettings.GetColour(wx.SYS_COLOUR_WINDOWTEXT))
        self.SetBackgroundColour(wx.SystemSettings.GetColour(wx.SYS_COLOUR_WINDOW))

        bSizer1 = wx.BoxSizer(wx.VERTICAL)

        self.m_scrolledWindow5 = wx.ScrolledWindow(
            self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.HSCROLL | wx.VSCROLL
        )
        self.m_scrolledWindow5.SetScrollRate(5, 5)
        bSizer14 = wx.BoxSizer(wx.VERTICAL)

        bSizer11 = wx.BoxSizer(wx.HORIZONTAL)

        self.m_staticDownIP1 = wx.StaticText(
            self.m_scrolledWindow5,
            wx.ID_ANY,
            _(u"下載SEL電驛事故"),
            wx.DefaultPosition,
            wx.DefaultSize,
            0,
        )
        self.m_staticDownIP1.Wrap(-1)

        self.m_staticDownIP1.SetFont(
            wx.Font(
                16,
                wx.FONTFAMILY_SWISS,
                wx.FONTSTYLE_NORMAL,
                wx.FONTWEIGHT_BOLD,
                False,
                "微軟正黑體",
            )
        )

        bSizer11.Add(
            self.m_staticDownIP1,
            0,
            wx.ALL | wx.ALIGN_CENTER_HORIZONTAL | wx.ALIGN_CENTER_VERTICAL,
            5,
        )

        bSizer14.Add(bSizer11, 0, wx.ALIGN_CENTER_HORIZONTAL, 5)

        bSizer2 = wx.BoxSizer(wx.HORIZONTAL)

        self.m_staticDownIP = wx.StaticText(
            self.m_scrolledWindow5,
            wx.ID_ANY,
            _(u"輸入下載IP (192.O.O.O)"),
            wx.DefaultPosition,
            wx.DefaultSize,
            0,
        )
        self.m_staticDownIP.Wrap(-1)

        self.m_staticDownIP.SetFont(
            wx.Font(
                14,
                wx.FONTFAMILY_SWISS,
                wx.FONTSTYLE_NORMAL,
                wx.FONTWEIGHT_NORMAL,
                False,
                "微軟正黑體",
            )
        )

        bSizer2.Add(self.m_staticDownIP, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)

        self.m_textCtrlDownIP = wx.TextCtrl(
            self.m_scrolledWindow5,
            wx.ID_ANY,
            wx.EmptyString,
            wx.DefaultPosition,
            wx.Size(180, -1),
            wx.TE_CENTER,
        )
        self.m_textCtrlDownIP.SetFont(
            wx.Font(
                14,
                wx.FONTFAMILY_SWISS,
                wx.FONTSTYLE_NORMAL,
                wx.FONTWEIGHT_NORMAL,
                False,
                "微軟正黑體",
            )
        )
        self.m_textCtrlDownIP.SetBackgroundColour(wx.SystemSettings.GetColour(wx.SYS_COLOUR_WINDOW))

        bSizer2.Add(self.m_textCtrlDownIP, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)

        bSizer14.Add(bSizer2, 0, wx.EXPAND, 5)

        bSizer22 = wx.BoxSizer(wx.HORIZONTAL)

        self.m_staticPort = wx.StaticText(
            self.m_scrolledWindow5,
            wx.ID_ANY,
            _(u"下載IP的port (建議用23)"),
            wx.DefaultPosition,
            wx.DefaultSize,
            0,
        )
        self.m_staticPort.Wrap(-1)

        self.m_staticPort.SetFont(
            wx.Font(
                14,
                wx.FONTFAMILY_SWISS,
                wx.FONTSTYLE_NORMAL,
                wx.FONTWEIGHT_NORMAL,
                False,
                "微軟正黑體",
            )
        )

        bSizer22.Add(self.m_staticPort, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)

        self.m_textCtrlPort = wx.TextCtrl(
            self.m_scrolledWindow5,
            wx.ID_ANY,
            _(u"23"),
            wx.DefaultPosition,
            wx.Size(50, -1),
            wx.TE_CENTER,
        )
        self.m_textCtrlPort.SetFont(
            wx.Font(
                14,
                wx.FONTFAMILY_SWISS,
                wx.FONTSTYLE_NORMAL,
                wx.FONTWEIGHT_NORMAL,
                False,
                "微軟正黑體",
            )
        )

        bSizer22.Add(self.m_textCtrlPort, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)

        bSizer14.Add(bSizer22, 0, wx.EXPAND, 5)

        bSizer211 = wx.BoxSizer(wx.HORIZONTAL)

        self.m_staticSample = wx.StaticText(
            self.m_scrolledWindow5,
            wx.ID_ANY,
            _(u"波形取樣率(Samples/Cyles)"),
            wx.DefaultPosition,
            wx.DefaultSize,
            0,
        )
        self.m_staticSample.Wrap(-1)

        self.m_staticSample.SetFont(
            wx.Font(
                14,
                wx.FONTFAMILY_SWISS,
                wx.FONTSTYLE_NORMAL,
                wx.FONTWEIGHT_NORMAL,
                False,
                "微軟正黑體",
            )
        )

        bSizer211.Add(self.m_staticSample, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)

        m_choiceSampleChoices = [_(u"4"), _(u"all")]
        self.m_choiceSample = wx.Choice(
            self.m_scrolledWindow5,
            wx.ID_ANY,
            wx.DefaultPosition,
            wx.DefaultSize,
            m_choiceSampleChoices,
            0,
        )
        self.m_choiceSample.SetSelection(0)
        self.m_choiceSample.SetFont(
            wx.Font(
                14,
                wx.FONTFAMILY_SWISS,
                wx.FONTSTYLE_NORMAL,
                wx.FONTWEIGHT_NORMAL,
                False,
                "微軟正黑體",
            )
        )

        bSizer211.Add(self.m_choiceSample, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)

        bSizer14.Add(bSizer211, 0, wx.EXPAND, 5)

        bSizer21 = wx.BoxSizer(wx.HORIZONTAL)

        self.m_staticCyles = wx.StaticText(
            self.m_scrolledWindow5,
            wx.ID_ANY,
            _(u"事件長度(Cyles)"),
            wx.DefaultPosition,
            wx.DefaultSize,
            0,
        )
        self.m_staticCyles.Wrap(-1)

        self.m_staticCyles.SetFont(
            wx.Font(
                14,
                wx.FONTFAMILY_SWISS,
                wx.FONTSTYLE_NORMAL,
                wx.FONTWEIGHT_NORMAL,
                False,
                "微軟正黑體",
            )
        )

        bSizer21.Add(self.m_staticCyles, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)

        self.m_textCtrlCyles = wx.TextCtrl(
            self.m_scrolledWindow5,
            wx.ID_ANY,
            wx.EmptyString,
            wx.DefaultPosition,
            wx.Size(50, -1),
            wx.TE_CENTER,
        )
        self.m_textCtrlCyles.SetFont(
            wx.Font(
                14,
                wx.FONTFAMILY_SWISS,
                wx.FONTSTYLE_NORMAL,
                wx.FONTWEIGHT_NORMAL,
                False,
                "微軟正黑體",
            )
        )

        bSizer21.Add(self.m_textCtrlCyles, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)

        bSizer14.Add(bSizer21, 0, wx.EXPAND, 5)

        bSizer2111 = wx.BoxSizer(wx.HORIZONTAL)

        self.m_staticTextEid = wx.StaticText(
            self.m_scrolledWindow5,
            wx.ID_ANY,
            _(
                u"選擇下載事故，（若無法決定，請維持空白）\n【,】分隔，【-】設定範圍，要下載最新三筆事故：【1-3】"
            ),
            wx.DefaultPosition,
            wx.DefaultSize,
            0,
        )
        self.m_staticTextEid.Wrap(-1)

        self.m_staticTextEid.SetFont(
            wx.Font(
                14,
                wx.FONTFAMILY_SWISS,
                wx.FONTSTYLE_NORMAL,
                wx.FONTWEIGHT_NORMAL,
                False,
                "微軟正黑體",
            )
        )

        bSizer2111.Add(self.m_staticTextEid, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)

        self.m_textCtrlEid = wx.TextCtrl(
            self.m_scrolledWindow5,
            wx.ID_ANY,
            wx.EmptyString,
            wx.DefaultPosition,
            wx.Size(-1, -1),
            0,
        )
        self.m_textCtrlEid.SetFont(
            wx.Font(
                14,
                wx.FONTFAMILY_SWISS,
                wx.FONTSTYLE_NORMAL,
                wx.FONTWEIGHT_NORMAL,
                False,
                "微軟正黑體",
            )
        )

        bSizer2111.Add(self.m_textCtrlEid, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)

        bSizer14.Add(bSizer2111, 0, wx.EXPAND, 5)

        bSizer212 = wx.BoxSizer(wx.HORIZONTAL)

        self.m_staticFloder = wx.StaticText(
            self.m_scrolledWindow5,
            wx.ID_ANY,
            _(u"選擇存檔路徑"),
            wx.DefaultPosition,
            wx.DefaultSize,
            0,
        )
        self.m_staticFloder.Wrap(-1)

        self.m_staticFloder.SetFont(
            wx.Font(
                14,
                wx.FONTFAMILY_SWISS,
                wx.FONTSTYLE_NORMAL,
                wx.FONTWEIGHT_NORMAL,
                False,
                "微軟正黑體",
            )
        )

        bSizer212.Add(self.m_staticFloder, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)

        self.m_textCtrlFloder = wx.TextCtrl(
            self.m_scrolledWindow5,
            wx.ID_ANY,
            wx.EmptyString,
            wx.DefaultPosition,
            wx.Size(-1, -1),
            0,
        )
        self.m_textCtrlFloder.SetFont(
            wx.Font(
                14,
                wx.FONTFAMILY_SWISS,
                wx.FONTSTYLE_NORMAL,
                wx.FONTWEIGHT_NORMAL,
                False,
                "微軟正黑體",
            )
        )

        bSizer212.Add(self.m_textCtrlFloder, 1, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)

        self.m_buttonFloder = wx.Button(
            self.m_scrolledWindow5, wx.ID_ANY, _(u"選擇路徑"), wx.DefaultPosition, wx.DefaultSize, 0
        )
        self.m_buttonFloder.SetFont(
            wx.Font(
                14,
                wx.FONTFAMILY_SWISS,
                wx.FONTSTYLE_NORMAL,
                wx.FONTWEIGHT_NORMAL,
                False,
                "微軟正黑體",
            )
        )

        bSizer212.Add(self.m_buttonFloder, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)

        bSizer14.Add(bSizer212, 0, wx.EXPAND, 5)

        bSizer2121 = wx.BoxSizer(wx.VERTICAL)

        bSizer2121.SetMinSize(wx.Size(-1, 50))
        self.m_buttonEXEFile = wx.Button(
            self.m_scrolledWindow5,
            wx.ID_ANY,
            _(u"選擇執行檔位置（若SEL Download執行檔路徑錯誤，才要設定）"),
            wx.DefaultPosition,
            wx.DefaultSize,
            0,
        )
        self.m_buttonEXEFile.SetFont(
            wx.Font(
                10,
                wx.FONTFAMILY_SWISS,
                wx.FONTSTYLE_NORMAL,
                wx.FONTWEIGHT_NORMAL,
                False,
                "微軟正黑體",
            )
        )

        bSizer2121.Add(self.m_buttonEXEFile, 0, wx.LEFT, 5)

        self.m_staticEXEFile = wx.StaticText(
            self.m_scrolledWindow5,
            wx.ID_ANY,
            wx.EmptyString,
            wx.DefaultPosition,
            wx.DefaultSize,
            0 | wx.FULL_REPAINT_ON_RESIZE,
        )
        self.m_staticEXEFile.Wrap(-1)

        self.m_staticEXEFile.SetFont(
            wx.Font(
                10,
                wx.FONTFAMILY_SWISS,
                wx.FONTSTYLE_NORMAL,
                wx.FONTWEIGHT_NORMAL,
                False,
                "微軟正黑體",
            )
        )

        bSizer2121.Add(self.m_staticEXEFile, 0, wx.EXPAND | wx.ALL, 5)

        bSizer14.Add(bSizer2121, 0, wx.EXPAND, 5)

        bSizer221 = wx.BoxSizer(wx.HORIZONTAL)

        self.m_buttonDownload = wx.Button(
            self.m_scrolledWindow5,
            wx.ID_ANY,
            _(u"下載事故波形"),
            wx.DefaultPosition,
            wx.DefaultSize,
            0,
        )
        self.m_buttonDownload.SetFont(
            wx.Font(
                14,
                wx.FONTFAMILY_SWISS,
                wx.FONTSTYLE_NORMAL,
                wx.FONTWEIGHT_NORMAL,
                False,
                "微軟正黑體",
            )
        )

        bSizer221.Add(self.m_buttonDownload, 1, wx.ALL | wx.ALIGN_BOTTOM, 5)

        self.m_buttonCancel = wx.Button(
            self.m_scrolledWindow5, wx.ID_ANY, _(u"結束軟體"), wx.DefaultPosition, wx.DefaultSize, 0
        )
        self.m_buttonCancel.SetFont(
            wx.Font(
                14,
                wx.FONTFAMILY_SWISS,
                wx.FONTSTYLE_NORMAL,
                wx.FONTWEIGHT_NORMAL,
                False,
                "微軟正黑體",
            )
        )

        bSizer221.Add(self.m_buttonCancel, 0, wx.ALL | wx.ALIGN_BOTTOM, 5)

        bSizer14.Add(bSizer221, 1, wx.EXPAND, 5)

        self.m_scrolledWindow5.SetSizer(bSizer14)
        self.m_scrolledWindow5.Layout()
        bSizer14.Fit(self.m_scrolledWindow5)
        bSizer1.Add(self.m_scrolledWindow5, 1, wx.EXPAND | wx.ALL, 5)

        self.SetSizer(bSizer1)
        self.Layout()

        self.Centre(wx.BOTH)

        # Connect Events
        self.Bind(wx.EVT_SIZE, self.on_resize)
        self.m_choiceSample.Bind(wx.EVT_CHOICE, self.OnSampleChoice)
        self.m_textCtrlFloder.Bind(wx.EVT_KILL_FOCUS, self.OnKillFocus_FloderText)
        self.m_buttonFloder.Bind(wx.EVT_BUTTON, self.OnFloderClick)
        self.m_buttonEXEFile.Bind(wx.EVT_BUTTON, self.OnEXEFileClick)
        self.m_buttonDownload.Bind(wx.EVT_BUTTON, self.OnDownloadClick)
        self.m_buttonCancel.Bind(wx.EVT_BUTTON, self.OnCancelClick)

    def __del__(self):
        pass

    # Virtual event handlers, override them in your derived class
    def on_resize(self, event):
        event.Skip()

    def OnSampleChoice(self, event):
        event.Skip()

    def OnKillFocus_FloderText(self, event):
        event.Skip()

    def OnFloderClick(self, event):
        event.Skip()

    def OnEXEFileClick(self, event):
        event.Skip()

    def OnDownloadClick(self, event):
        event.Skip()

    def OnCancelClick(self, event):
        event.Skip()
