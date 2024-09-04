# Solana CA Screener

## About
Bulk scans and automatically detect potential and definite Solana Blockchain CA rug pulls, and scams. 
This is done through the use of various API's to assess a contract and determine it's validity

> [!NOTE]  
> This repository does not and will not provide a method of fetching contracts to scan, though you are free to fork this repository and implement that functionality yourself.

Currently supports:
- Raydium
- Pump Fun

## Demo Video

### Getting Started

1. Clone the repository.
```sh
git clone https://github.com/PadraigHalstead/solana-ca-screener.git
```

2. Install dependencies from `requirements.txt`

3. Configure enviornment variables

Solana FM API Key can be obtained for free here: https://portal.solana.fm/

For SolScan:
- Go to Solscan.io
- Press F12
- Click network tab
- Refresh the page
- Click on the document and headings as shown and copy the cookie to your .env file.

![SolScan Instructions](https://github.com/PadraigHalstead/solana-ca-screener/blob/main/docs/cookie.png?raw=true)

5. Run the program

6. Add Contract Addresses to `Potential.csv`
