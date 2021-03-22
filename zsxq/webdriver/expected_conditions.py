from selenium.webdriver.support.expected_conditions import _find_element


class element_is_complete(object):
    """
    期望指定的元素加载完毕[1]，并返回该元素

    :param locator: 指定元素的选择器

    References:
        [1] http://www.w3school.com.cn/jsref/prop_img_complete.asp
        [2] selenium.webdriver.support.expected_conditions
    """

    def __init__(self, locator):
        self.locator = locator

    def __call__(self, driver):
        return _element_if_complete(_find_element(driver, self.locator))


def _element_if_complete(element, complete=True):
    """
    Shortcut: 元素complete属性符合要求时，返回该元素

    :param element: 指定元素
    :param complete: 指定状态
    :return: 状态符合时返回element
    """

    return element if element.get_property('complete') == complete else False


class cookie_is_set(object):
    """
    期望指定的cookie被设置，并返回该cookie值

    :param name: cookie名
    """

    def __init__(self, name):
        self.name = name

    def __call__(self, driver):
        return driver.get_cookie(self.name) or False
