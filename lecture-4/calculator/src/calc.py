import flet as ft
import math


class CalcButton(ft.ElevatedButton):
    def __init__(self, text, button_clicked, expand=1):
        super().__init__()
        self.text = text
        self.expand = expand
        self.on_click = button_clicked
        self.data = text
        self.height = 60
        self.content = ft.Text(
            text, 
            size=20, 
            weight=ft.FontWeight.W_500,
            text_align=ft.TextAlign.CENTER
        )


class DigitButton(CalcButton):
    def __init__(self, text, button_clicked, expand=1):
        CalcButton.__init__(self, text, button_clicked, expand)
        self.bgcolor = ft.Colors.GREY_800
        self.color = ft.Colors.WHITE
        self.style = ft.ButtonStyle(
            shape=ft.RoundedRectangleBorder(radius=15),
            elevation=3,
            animation_duration=100,
        )


class ActionButton(CalcButton):
    def __init__(self, text, button_clicked):
        CalcButton.__init__(self, text, button_clicked)
        self.bgcolor = ft.Colors.ORANGE_600
        self.color = ft.Colors.WHITE
        self.style = ft.ButtonStyle(
            shape=ft.RoundedRectangleBorder(radius=15),
            elevation=5,
            animation_duration=100,
        )


class ExtraActionButton(CalcButton):
    def __init__(self, text, button_clicked):
        CalcButton.__init__(self, text, button_clicked)
        self.bgcolor = ft.Colors.GREY_600
        self.color = ft.Colors.WHITE
        self.style = ft.ButtonStyle(
            shape=ft.RoundedRectangleBorder(radius=15),
            elevation=3,
            animation_duration=100,
        )


class SciCalcButton(CalcButton):
    def __init__(self, text, button_clicked):
        CalcButton.__init__(self, text, button_clicked)
        self.bgcolor = ft.Colors.BLUE_700
        self.color = ft.Colors.WHITE
        self.style = ft.ButtonStyle(
            shape=ft.RoundedRectangleBorder(radius=15),
            elevation=4,
            animation_duration=100,
        )


class CalculatorApp(ft.Container):
    # application's root control (i.e. "view") containing all other controls
    def __init__(self):
        super().__init__()
        self.reset()

        self.result = ft.Text(
            value="0", 
            color=ft.Colors.WHITE, 
            size=36,
            weight=ft.FontWeight.W_300,
            text_align=ft.TextAlign.RIGHT
        )
        self.history = ft.Text(
            value="", 
            color=ft.Colors.GREY_400, 
            size=16,
            text_align=ft.TextAlign.RIGHT
        )
        self.width = 450
        self.bgcolor = ft.Colors.GREY_900
        self.border_radius = ft.border_radius.all(25)
        self.padding = 25
        self.shadow = ft.BoxShadow(
            spread_radius=1,
            blur_radius=15,
            color=ft.Colors.BLACK26,
            offset=ft.Offset(0, 8),
        )
        self.content = ft.Column(
            controls=[
                ft.Container(
                    content=ft.Column([
                        ft.Row(controls=[self.history], alignment="end"),
                        ft.Row(controls=[self.result], alignment="end"),
                    ]),
                    height=100,
                    padding=ft.padding.all(15),
                    bgcolor=ft.Colors.GREY_800,
                    border_radius=ft.border_radius.all(15),
                    margin=ft.margin.only(bottom=20)
                ),
                ft.Row(
                    controls=[
                        SciCalcButton(text="√", button_clicked=self.button_clicked),#平方根計算
                        SciCalcButton(text="x²", button_clicked=self.button_clicked),#二乗計算
                        SciCalcButton(text="1/x", button_clicked=self.button_clicked),#逆数計算
                        SciCalcButton(text="sin", button_clicked=self.button_clicked),#正弦計算
                        SciCalcButton(text="cos", button_clicked=self.button_clicked),#余弦計算
                    ],
                    spacing=8
                ),
                ft.Row(
                    controls=[
                        ExtraActionButton(text="AC", button_clicked=self.button_clicked),
                        ExtraActionButton(text="⌫", button_clicked=self.button_clicked),
                        ExtraActionButton(text="%", button_clicked=self.button_clicked),
                        ActionButton(text="÷", button_clicked=self.button_clicked),
                    ],
                    spacing=8
                ),
                ft.Row(
                    controls=[
                        DigitButton(text="7", button_clicked=self.button_clicked),
                        DigitButton(text="8", button_clicked=self.button_clicked),
                        DigitButton(text="9", button_clicked=self.button_clicked),
                        ActionButton(text="×", button_clicked=self.button_clicked),
                    ],
                    spacing=8
                ),
                ft.Row(
                    controls=[
                        DigitButton(text="4", button_clicked=self.button_clicked),
                        DigitButton(text="5", button_clicked=self.button_clicked),
                        DigitButton(text="6", button_clicked=self.button_clicked),
                        ActionButton(text="−", button_clicked=self.button_clicked),
                    ],
                    spacing=8
                ),
                ft.Row(
                    controls=[
                        DigitButton(text="1", button_clicked=self.button_clicked),
                        DigitButton(text="2", button_clicked=self.button_clicked),
                        DigitButton(text="3", button_clicked=self.button_clicked),
                        ActionButton(text="+", button_clicked=self.button_clicked),
                    ],
                    spacing=8
                ),
                ft.Row(
                    controls=[
                        ExtraActionButton(text="±", button_clicked=self.button_clicked),
                        DigitButton(text="0", button_clicked=self.button_clicked),
                        DigitButton(text=".", button_clicked=self.button_clicked),
                        ActionButton(text="=", button_clicked=self.button_clicked),
                    ],
                    spacing=8
                ),
            ],
            spacing=12,
            tight=True
        )

    def button_clicked(self, e):
        data = e.control.data
        print(f"Button clicked with data = {data}")
        
        # エラー状態またはAC（全クリア）
        if self.result.value == "Error" or data == "AC":
            self.result.value = "0"
            self.history.value = ""
            self.reset()

        # バックスペース機能
        elif data == "⌫":
            if len(self.result.value) > 1:
                self.result.value = self.result.value[:-1]
            else:
                self.result.value = "0"

        # 数字と小数点の入力
        elif data in ("1", "2", "3", "4", "5", "6", "7", "8", "9", "0", "."):
            if data == "." and "." in self.result.value:
                return  # 既に小数点がある場合は追加しない
            if self.result.value == "0" or self.new_operand:
                self.result.value = data if data != "." else "0."
                self.new_operand = False
            else:
                self.result.value = self.result.value + data

        # 四則演算
        elif data in ("+", "−", "×", "÷"):
            # 履歴表示の更新
            if not self.new_operand:
                self.history.value = f"{self.result.value} {data}"
            
            self.result.value = self.calculate(
                self.operand1, float(self.result.value), self.operator
            )
            self.operator = data
            if self.result.value == "Error":
                self.operand1 = "0"
            else:
                self.operand1 = float(self.result.value)
            self.new_operand = True

        # 等号（計算実行）
        elif data == "=":
            if not self.new_operand:
                self.history.value = f"{self.history.value} {self.result.value} ="
            self.result.value = self.calculate(
                self.operand1, float(self.result.value), self.operator
            )
            self.reset()

        # パーセント
        elif data == "%":
            self.result.value = self.format_number(float(self.result.value) / 100)
            self.reset()

        # プラスマイナス切り替え
        elif data == "±":
            if float(self.result.value) > 0:
                self.result.value = "-" + str(self.result.value)
            elif float(self.result.value) < 0:
                self.result.value = str(self.format_number(abs(float(self.result.value))))

        # 科学計算機能
        elif data == "√":
            try:
                value = float(self.result.value)
                if value < 0:
                    self.result.value = "Error"
                else:
                    self.history.value = f"√({self.result.value})"
                    self.result.value = self.format_number(math.sqrt(value))
            except:
                self.result.value = "Error"
            self.reset()

        elif data == "x²":
            self.history.value = f"({self.result.value})²"
            self.result.value = self.format_number(float(self.result.value) ** 2)
            self.reset()

        elif data == "1/x":
            if float(self.result.value) == 0:
                self.result.value = "Error"
            else:
                self.history.value = f"1/({self.result.value})"
                self.result.value = self.format_number(1 / float(self.result.value))
            self.reset()

        elif data == "sin":
            self.history.value = f"sin({self.result.value})"
            self.result.value = self.format_number(math.sin(math.radians(float(self.result.value))))
            self.reset()

        elif data == "cos":
            self.history.value = f"cos({self.result.value})"
            self.result.value = self.format_number(math.cos(math.radians(float(self.result.value))))
            self.reset()

        self.update()

    def format_number(self, num):
        if num % 1 == 0:
            return int(num)
        else:
            return num

    def calculate(self, operand1, operand2, operator):
        try:
            if operator == "+":
                return self.format_number(operand1 + operand2)
            elif operator == "−":
                return self.format_number(operand1 - operand2)
            elif operator == "×":
                return self.format_number(operand1 * operand2)
            elif operator == "÷":
                if operand2 == 0:
                    return "Error"
                else:
                    return self.format_number(operand1 / operand2)
        except:
            return "Error"

    def reset(self):
        self.operator = "+"
        self.operand1 = 0
        self.new_operand = True


def main(page: ft.Page):
    page.title = "🔢 Beautiful Calculator"
    page.bgcolor = ft.Colors.GREY_100
    page.window.width = 500
    page.window.height = 700
    page.window.resizable = False
    page.padding = 20
    
    # create application instance
    calc = CalculatorApp()

    # add application's root control to the page with centering
    page.add(
        ft.Container(
            content=calc,
            alignment=ft.alignment.center,
        )
    )


ft.app(target=main)