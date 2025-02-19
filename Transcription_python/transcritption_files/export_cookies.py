import browser_cookie3
import http.cookiejar

cookies = browser_cookie3.chrome(domain_name='.youtube.com')
cookie_jar = http.cookiejar.MozillaCookieJar('cookies.txt')
for cookie in cookies:
    cookie_jar.set_cookie(cookie)
cookie_jar.save()