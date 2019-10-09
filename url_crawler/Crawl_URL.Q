[General]
SyntaxVersion=2
BeginHotkey=121
BeginHotkeyMod=0
PauseHotkey=0
PauseHotkeyMod=0
StopHotkey=123
StopHotkeyMod=0
RunOnce=1
EnableWindow=
MacroID=4ed254d6-e5ce-4cfb-8653-7e26c31d48b5
Description=我的腳本1
Enable=1
AutoRun=0
[Repeat]
Type=0
Number=1
[SetupUI]
Type=2
QUI=
[Relative]
SetupOCXFile=
[Comment]

[Script]
Randomize
Dim Stop, MouseWheelSize, PageWidth, init_X, init_Y, rate_X, rate_Y, Bar_X, Bar_Y1, Bar_Y2, Error_X, Error_Y1, Error_Y2, Last_Y, Scroll_Time, Page, Line_Color, Bar_Color, ScreenShot_X1, ScreenShot_X2, ScreenShot_Y1, ScreenShot_Y2, Refresh_X, Refresh_Y, articles
rate_X = Plugin.Sys.GetScRX / 1915
rate_Y = Plugin.Sys.GetScRY / 951
AccountNumber  = 1
PageWidth = 106
init_X = 88
init_Y = 100
Bar_X = 1143
Bar_Y1 = 80
Bar_Y2 = 818
Account_X = 525
Account_Y1 = 64
Account_Y2 = 810
Account_BarX = 1145
Account_BarY = 809
Account_Bar_Color = "D2D2D2"
AccountWidth = 100
Last_Y = -1
Scroll_Time = 1
Page = 1
Bar_Color = "C9C3C1"
Bar_Color2 = "BCBCBC"
LinkColor = "FF902C"
Line_Color = "F2F1F1"
Line_Color2 = "ECEAEA"
ScreenShot_X1 = 10
ScreenShot_X2 = 250
moves = 0
Refresh_X = 83
Refresh_Y = 53
Line_X = 595
Retry = 0
Back_X = 36
Back_Y = 52
num = 0

LockMouse

LogStart "C:\Users\ohlab\Desktop\weixin.log"

Dim MyDate

MyDate = CStr(Date)

Function Main()
	num = 0

	Folder = "C:\Users\ohlab\Desktop\urls"
	
	Folder2 = "C:\Users\ohlab\Desktop\Data"
	
	r = Lib.文件.判斷文件夾是否存在(Folder)
	
	If r = 0 Then 
		Call Plugin.File.CreateFolder(Folder)
	Else 
		TracePrint "No"
	End If
	
	r = Lib.文件.判斷文件夾是否存在(Folder2)
	
	If r = 0 Then 
		Call Plugin.File.CreateFolder(Folder2)
	Else 
		TracePrint "No"
	End If
	
	Dim intX, intY, times, t
	Hwnd = Plugin.Window.Find("CefWebViewWnd", "WeChat")
	Call Plugin.Window.Max(Hwnd)
	intX = 0
	intY = 0 
	k = 0
	Do While True
		If k > 2 Then 		
			FindPic 0, 0, Bar_X, Bar_Y2, "Attachment:\account_ban.bmp", 0.99, Ban_AccountX, Ban_AccountY
			KeyDown "Alt", 1
			KeyPress "F4", 1
			KeyUp "Alt", 1
			TracePrint "Loading Next Page Error. Again"
			If Ban_AccountX > 0 and Ban_AccountY > 0 Then 
				Delay 24 * 60 * 60 * 1000
				TracePrint "Banned Sleep one day."
			End If
			Main = - 1 
			Delay 200
			Exit Function
		End If
		If WaitForBack = 1 Then 
			Exit Do
		Else 
			k = k + 1
			TracePrint "Refresh"
			MoveTo Refresh_X, Refresh_Y
			Delay 500
			LeftClick 1
		End If
	Loop
	
	Delay Int((500 * Rnd) + 2000)
	
	k = 0
	
	Do While True
		TracePrint "Finding Bar"
		If k > 2 Then 
			KeyDown "Alt", 1
			KeyPress "F4", 1
			KeyUp "Alt", 1
			TracePrint "Finding No Bar. Again"
			Main = - 1 
			Delay 200
			Exit Function
		End If
		FindColor Bar_X, Bar_Y1, Bar_X, Bar_Y2, Bar_Color, X, Y
		FindColor Bar_X, Bar_Y1, Bar_X, Bar_Y2, Bar_Color2, X2, Y2
		If X < 0 and Y < 0 and X2 < 0 and Y2 < 0 Then 
			TracePrint "Refresh"
			MoveTo Refresh_X, Refresh_Y
			Delay 500
			LeftClick 1
			k = k + 1
		Else
			TracePrint "Finish"
			Exit Do
		End If
		If WaitForBack = 1 Then 
			Exit Do
		Else 
			k = k + 1
			TracePrint "Refresh"
			MoveTo Refresh_X, Refresh_Y
			Delay 500
			LeftClick 1
		End If
	Loop
	
	
	Call MoveBar()
	
	
	Delay Int((500 * Rnd) + 1000)
	
	MoveTo init_X,init_Y
	Delay 3500
	Call Plugin.Pic.PrintScreen(ScreenShot_X1, (intY + 19), ScreenShot_X2, (intY - 43), Folder & "\next" & AccountNumber & ".bmp")
	times = 0
	FindColor Bar_X, Bar_Y1, Bar_X, Bar_Y2, Bar_Color, X, Y
	Last_Y = Y
	X = 0
	Y = 0
	Delay 2000
	getpic = 0
	Dim alert
	alert = 0
	Do Until getpic = 1
		Hwnd = Plugin.Window.Find("#32770", "JavaScript Alert - https://mp.weixin.qq.com")
		If Hwnd > 0 Then 
			TracePrint "alert :" & alert
			If alert = 1 Then 
				KeyDown "Alt", 1
				KeyPress "F4", 1
				Delay 200
				KeyPress "F4", 1
				KeyUp "Alt", 1
				//Hwnd = Plugin.Window.Find("CefWebViewWnd", "WeChat")
				//Plugin.Window.Close (Hwnd)
				TracePrint "Touch End Loading Error. Again"
				Main = - 1 
				Delay 200
				Exit Function
			Else 
				alert = 1
				KeyPress "Enter", 1
			End If
			//Plugin.Window.Close (Hwnd)
			
		Else 
			TracePrint "No Alert"
			alert = 0
			Delay 300
		End If
		Hwnd = Plugin.Window.Find("ImagePreviewWnd", "圖片查看")
		If Hwnd > 0 Then 
			
			Call Plugin.Window.Hide(Hwnd)
			MoveTo 500, 10
			Delay 100
			LeftClick 1
			//Call Plugin.Window.Active(Hwnd)
			//KeyDown "Alt", 1
			//KeyPress "F4", 1
			//KeyUp "Alt", 1
			Delay 200
		End If
		
		Delay 200
		
		FindColor Line_X, Bar_Y1, Line_X, Bar_Y2, Line_Color, intX, intY
		
		TracePrint "Y: " & intY
		TracePrint "articles: " & articles
		TracePrint "Finding Next Picture"
		//Delay 100
		//FindPic ScreenShot_X1 - 10, intY + 1, ScreenShot_X2 + 10, intY  + PageWidth - 1, "D:\按鍵精靈\next.bmp", 0.8, picX, picY
		FindPic ScreenShot_X1 - 10, intY - 10, ScreenShot_X2 + 200, intY  + PageWidth + 20 , Folder2 & "\next" & AccountNumber & ".bmp", 0.985, picX, picY
		//Call Plugin.Pic.PrintScreen(ScreenShot_X1 - 10, intY + 1, ScreenShot_X2 + 10, intY + PageWidth - 1, "C:\Users\404411240\Documents\now.bmp")
		k = 0
		
		If picX < 0 and picY < 0 Then 
			//Call MoveBar()
			//Delay 500
			MoveTo init_X, init_Y
			Delay 30
			//FindColor Line_X, Bar_Y1, Line_X, Bar_Y2, Line_Color, X1, Y1
			//MouseWheel - 1 
			FindColor Line_X, Bar_Y1, Line_X, Bar_Y2, Line_Color, intX, intY
			
			multi = 1
			Do While True
				If multi = 5 Then 
					Exit Do
				End If
				FindPic ScreenShot_X1 - 10, intY - 10, ScreenShot_X2 + 200, intY + (multi + 1) * PageWidth + 20, Folder & "\next.bmp", 0.985, picX, picY
				If picX < 0 and picY < 0 Then 
					multi = multi + 1
				Else 
					Exit Do
				End If
			Loop
			
			TracePrint "multi: " & multi
			//Delay 100
			For multi
				MouseWheel - 1 
				Delay 30
			Next
			
			moves = moves + multi
			
			Delay 200
		
		 	
			Do While True
				If k > 2 Then 
					KeyDown "Alt", 1
					KeyPress "F4", 1
					KeyUp "Alt", 1
					TracePrint "Loading Next Page Error. Again"
					Main = - 1 
					Delay 200
					Exit Function
				End If
				If WaitForBack = 1 Then
					Exit Do
				Else 
				    k = k + 1
				    TracePrint "Loading Next Page Error. Refresh"
					MoveTo Refresh_X, Refresh_Y
					LeftClick 1
				End If
			Loop
			//MouseWheel - 1 
			
			//Delay 50
			//MouseWheel -1
			//KeyPress "Down", 1
		ElseIf moves > 50 Then
			getpic = 1
		Else 
			getpic = 1
		End If
	Loop
		TracePrint "Got it"
	Call GetPage()
	KeyDown "Alt", 1
	KeyPress "F4", 1
	KeyUp "Alt", 1
	Main = 1
End Function


Sub MoveBar()
	TracePrint "Move Bar"
	FindColor Line_X, Bar_Y1, Line_X, Bar_Y2, Line_Color, intX, intY
	Last_Y = intY
	X = - 1 
	Y = - 1 
	GetColor = "000000"
	
	
	
	Do Until GetColor = Bar_Color or GetColor = Bar_Color2
		
		FindColor Bar_X, Bar_Y1, Bar_X, Bar_Y2, Bar_Color, X, Y
		Delay 200
		If X < 0 and Y < 0 Then 
			FindColor Bar_X, Bar_Y1, Bar_X, Bar_Y2, Bar_Color2, X, Y
		End If
		GetColor = GetPixelColor(X, Y)
		
	Loop
	
	//TracePrint Y
	
	LoadingTime = 0
	t = Timer()
	//MessageBox X
	//MessageBox Y
	
	MoveTo X, Y
	LeftDown 1
	
	Do Until intY > Last_Y
		Delay 50
		MoveR 0, 1
		GetColor = GetPixelColor(Bar_X, Bar_Y2)
		If GetColor = Bar_Color Then 
			Page = Page + 1
		End If
		Do Until GetColor <> Bar_Color
			Hwnd = Plugin.Window.Find("#32770", "JavaScript Alert - https://mp.weixin.qq.com")
			If Hwnd > 0 Then 
				LeftUp 1
				Delay 100
				Exit Sub
			End If
			Delay 100
			GetColor = GetPixelColor(Bar_X, Bar_Y2)
		Loop
		
		Last_Y = intY
		FindColor Line_X, Bar_Y1, Line_X, Bar_Y2, Line_Color, intX, intY
	Loop
	
	LeftUp 1
	
	//Delay 500
End Sub

Function WaitForBack()
	Dim LoadingTime
	
	LoadingTime = 0
	t = Timer()
	
	
	intX = 0
	intY = 0
	
	Do Until (intX > 0 and intY > 0) or LoadingTime > 20
		FindColor Line_X, Bar_Y1, Line_X, Bar_Y2, Line_Color, intX, intY
		LoadingTime = Timer() - t
	Loop
	
	If LoadingTime > 20 Then 
		WaitForBack = -1
	Else 
		WaitForBack = 1
	End If
End Function

Function WaitForGettingPage()
	Dim X, Y1, Y2
	X = 50
	Y1 = 77
	Y2 = 905
	
	Dim LoadingTime
	
	
	
	LoadingTime = 0
	t = Timer()
	
	intX = 0
	intY = 0
	
	Do Until (intX < 0 and intY < 0) or LoadingTime > 5
		FindColor X, Y1, X, Y2, Line_Color, intX, intY
		LoadingTime = Timer() - t
	Loop
	
	If LoadingTime > 5 Then 
		WaitForGettingPage = -1
	Else 
		WaitForGettingPage = 1
	End If
	
End Function

Function Scroll()
	Dim up_rate, longdelay_rate, wait, dice
	uprate = 10
	longdelay_rate = 30
	MouseWheel - 1
	Delay Rnd * 2 + 1
	MouseWheel - 1
	Delay Rnd * 20 + 18
	dice = Int((99 * Rnd) + 1)
	If dice <= longdelay_rate Then 
		Delay 400 * Rnd + 400
		longdelay_rate = 30
	Else 
		Delay 200 * Rnd + 20
		longdelay_rate = longdelay_rate + 10
	End If
	dice = Int((99 * Rnd) + 1)
	If dice <= uprate Then 
		MouseWheel 1
		Delay Rnd * 2 + 1
		MouseWheel 1
		Delay Rnd * 20 + 18
		uprate = 10
		Delay 200 * Rnd + 20
	Else 
		uprate = uprate + 8
	End If
End Function


Sub GetPage()
	Dim dice
	filename = Folder & "\" & MyDate & "_" & AccountNumber & ".txt"
	
	Const write = 2
	Dim fso, f
	Set fso = CreateObject("Scripting.FileSystemObject")
	Set f = fso.OpenTextFile(filename, write, True)
	f.Write " "
	f.Close 
	KeyDown 17, 1
	KeyPress 65, 1
	KeyUp 17, 1
	Delay 200
	KeyDown 17, 1
	KeyPress 67, 1
	KeyUp 17, 1
	RunApp filename
	
	
	Delay 1000
	KeyDown 17, 1
	KeyPress 82, 1
	KeyUp 17, 1
	Delay 200
	KeyDown 17, 1
	KeyPress 83, 1
	KeyUp 17, 1
	Delay 300
	KeyDown 17, 1
	KeyPress 87, 1
	KeyUp 17, 1
	Delay 300
	KeyDown 18, 1
	KeyPress 115, 1
	KeyUp 18, 1
	TracePrint "Save article as " & MyDate & "_" & AccountNumber & ".txt"
	TracePrint "Save Article"
End Sub

Sub MouseMove(mouseY)
	GetCursorPos x, y
	//TracePrint "mouseY: " & mouseY
	//TracePrint "X: " & x & " Y: " & y
	Do Until y = mouseY
		If y > mouseY Then 
			y = y - 1
		ElseIf y < mouseY Then
			y = y + 1
		End If
		If x <= Account_X - 100 Then 
			x = x + 1
		ElseIf x >= Account_X + 500 Then
			x = x - 1
		End If
		MoveTo x, y
		Delay Rnd * 30
	Loop
	//TracePrint "X: " & x & " Y: " & y
	If x <= Account_X - 100 or x >= AccountX + 500 Then 
		MoveTo Account_X + Int(100 * Rnd), mouseY
	End If
	
End Sub

Sub RandomMove()
	MoveTo 578, 298
	Delay 120
	MoveTo 577, 298
	Delay 101
	MoveTo 503, 258
	Delay 108
	MoveTo 444, 139
	Delay 98
	MoveTo 756, 56
	Delay 102
	MoveTo 801, 82
	Delay 100
	MoveTo 779, 151
	Delay 106
	MoveTo 732, 184
	Delay 101
	MoveTo 691, 168
	Delay 101
	MoveTo 687, 118
	Delay 107
	MoveTo 763, 156
	Delay 101
	MoveTo 745, 220
	Delay 105
	MoveTo 713, 238
End Sub

Finish = -1
Done = -1
nomove = 0


While 1
	articles = 0
	If AccountNumber = 56 Then 
		MoveTo 338, 395
		LeftClick 1
		KeyPress "Home", 1
		UnlockMouse
		Delay 24 * 60 * 60 * 1000
		LockMouse
		AccountNumber = 1
		nomove = 0
		TracePrint "Sleep 1 day"
	End If
	TracePrint "Start Accountnumber : " & AccountNumber
	FindColor Account_X, Account_Y1, Account_X, Account_Y2, LinkColor, X, Y
	LastY = Y
	While Finish = - 1 
    	Hwnd = Plugin.Window.Find("WeChatMainWndForPC", "WeChat")
    	Call Plugin.Window.Max(Hwnd)
    	Call RandomMove()
		Call MouseMove(Y + AccountWidth * nomove + Int(30 * Rnd))
    	//MoveTo X + Int(100 * Rnd), Y + AccountWidth * nomove + Int(50 * Rnd)
    	Delay 200
    	LeftClick 1
    	/*Finish = 1
    	Delay 1000
    	KeyDown "Alt", 1
		KeyPress "F4", 1
		KeyUp "Alt", 1*/
		Finish = Main
	    Retry = 1
	Wend
	Delay 60 * 1000 * Rnd
	Finish = - 1 
	Retry = 0
	AccountNumber = AccountNumber + 1
	MoveTo 700, 18
	LeftClick 1
	MoveTo X - 20, Y
	Delay 1000
	Do While 1
		FindColor Account_BarX, Account_Y1, Account_BarX, Account_Y2, Account_Bar_Color, BarX, LastBarY
		While LastBarY = - 1 
		    TracePrint "LastBarY: " & LastBarY
			Call RandomMove()
			FindColor Account_BarX, Account_Y1, Account_BarX, Account_Y2, Account_Bar_Color, BarX, LastBarY
			TracePrint "Random Moved LastBarY: " & LastBarY
		Wend
		If GetPixelColor(Account_BarX, Account_BarY) = Account_Bar_Color Then
			TracePrint "Bar Slide to End"
			nomove = nomove + 1
			Exit Do
		End If
		Do While 1
			MouseWheel - 1 
			Delay 1000
			FindColor Account_BarX, Account_Y1, Account_BarX, Account_Y2, Account_Bar_Color, BarX, BarY
			TracePrint "BarY: " & BarY
			If BarY <> LastBarY Then 
				Exit Do
			End If
		Loop
		FindColor Account_X, Account_Y1, Account_X, Account_Y2, LinkColor, X, Y
		If LastY < Y Then 
			TracePrint "Goto Next Account"
			Exit Do
		End If
		LastY = Y
	Loop
Wend
