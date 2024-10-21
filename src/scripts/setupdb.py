from pip._internal.operations import freeze
import sqlite3

if __name__ == "__main__":
    con = sqlite3.connect("envs.db")
    cur = con.cursor()
    cur.execute("CREATE TABLE IF NOT EXISTS packages (name TEXT, path TEXT)")
    pkgs = freeze.freeze()
    target_pkgs = ["pymatcal", "pyrecon", "pyphantom", "pyspebt"]
    for pkg in pkgs:
        for option in target_pkgs:
            if pkg.startswith(option):
                path = pkg.split("@ file://")[1]
                cur.execute(
                    "INSERT INTO packages (name, path) VALUES (?, ?)", (option, path)
                )
    con.commit()
    con.close()
