from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from selenium import webdriver

def ds_login(driver=None, login=None, password=None):
    if driver is None:
        driver = webdriver.Chrome()
        driver.get(f"https://discord.com/channels/@me")

    print("[DS-LOGIN] Вход...")

    try:
        continue_button = WebDriverWait(driver, 3).until(
            EC.presence_of_element_located((By.CSS_SELECTOR,
                                            'button.marginTop8__83d4b.marginCenterHorz__4cf72.linkButton_ba7970.button_afdfd9.lookLink__93965.lowSaturationUnderline__95e71.colorLink_b651e5.sizeMin__94642.grow__4c8a4'))
        )
        continue_button.click()
    except Exception:
        # print("no continue key")
        pass


    try:
        login_button_1 = WebDriverWait(driver, 3).until(
            EC.presence_of_element_located((By.CSS_SELECTOR,
                                            'button.button_afdfd9.lookFilled__19298.colorPrimary__6ed40.sizeMedium_c6fa98.grow__4c8a4'))
        )
        login_button_1.click()
        print("[DS-LOGIN] Нужно войти снова")
    except:
        pass

    try:
        email_input = WebDriverWait(driver, 3).until(
            EC.presence_of_element_located((By.CSS_SELECTOR,
                                            'input.inputDefault__80165.input_d266e7'))
        )
        email_input.click()

        if login is None or password is None:
            print("Не указан логин или пароль в параметрах login, password")
            return Exception

        email_input.send_keys(login)

        driver.save_screenshot("QR.png")
        print("[DS-LOGIN] QR сохранён")

        password_field = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR,
                                            'input.inputDefault__80165.input_d266e7'))
        )
        password_field.click()
        password_field.send_keys(password)

        login_button = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR,
                                            'button.marginBottom8_f4aae3.button__47891.button_afdfd9.lookFilled__19298.colorBrand_b2253e.sizeLarge__9049d.fullWidth__7c3e8.grow__4c8a4'))
        )
        login_button.click()

        # если есть 2-х факторка
        try:
            auth_code_field = WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.CSS_SELECTOR,
                                                "input.inputDefault__80165.input_d266e7"))
            )
            auth_code_field.send_keys(input("6-значный код подтверждения:"))
            time.sleep(3)
            button = driver.find_element(by=By.CSS_SELECTOR,
                                         value="button.button_afdfd9.lookFilled__19298.colorBrand_b2253e.sizeMedium_c6fa98.grow__4c8a4")
            button.click()
        except Exception as e:
            # print("no auth code", str(e)[:50])
            pass

        print("[DS-LOGIN] Выполнен вход!")
    except Exception:
        print("[DS-LOGIN] Не требуется вход")