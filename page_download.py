import sys
import requests



def main():
    if len(sys.argv) < 2:
        print("not enough args")
        exit()
    name = sys.argv[1]
    name_url = name.replace(" ", "-").replace("...", "").replace("'", "").replace("#","").lower()
    result = requests.get(f"https://www.deepcreek.com/vacation-rentals/{name_url}")
    cabin_file_name = name_url + ".html"
    with open(cabin_file_name, 'w') as f:
        f.write(result.content.decode())
    
    print(f"Downloaded to {cabin_file_name}")

if __name__ == "__main__":
    main()