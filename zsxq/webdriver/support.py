from selenium import webdriver


class AutoClosableChrome(webdriver.Chrome):
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.quit()
