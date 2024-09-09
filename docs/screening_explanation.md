# Screening Explanation

This document outlines the reasoning behind each check inside the program.

> [!NOTE]  
> As a general rule: A contract that is legitimate should not have this kind of shady behaviour around it. But of course, there are exceptions which cannot be account for. This is designed to detect as many potentially fraudulent contracts as possible.



## Pump.fun Check

Pump.fun can be hit and miss. Sometimes its really good and sometimes its full of scams (like when influencers join the space).

You can choose to opt-in or opt-out of these tokens if you do not think its worth it.

This part of the program will determine if its a pump.fun launch or not.


## RugCheck

This part of the program will check various contract related information.

### Mint Authority

A contract with mint authority enabled is extremely dangerous. This means the developer/creator of the contract can "mint" or create more tokens, deflating the current value of your tokens.

### Freeze Authority

Also very dangerous. Developer/creator can "Freeze" the contract, preventing you from being able to trade your tokens.

### Mutable Metadata

Not the worst thing in the world. Creator can edit picture description etc. This is often left enabled to rug a contract and change its details again into a new contract, without needing to put the money up to mint a new token.

### Low Liquidiy

Token with low liquidity means that trading amounts out can be limited based on the size of the liquidity pool. 

### Unlocked Liquidity

Liquidity pool being unlocked means the creator can pull the liquidity from the contract, stopping you from swapping your tokens, effectively rugging the contract.

### Insider Holders

Insiders are wallets usually linked to the creator/developer, in an attempt to hide their true holdings of a token. Possibility of them selling all of their tokens from these wallets.

## Top Holders

This part of the program checks information related to the holdings of the top wallets.

### Number of holders

Tokens that are very new (less than a day old) that have a lot of holders, indicates a lot of bot trading is happening and are not actual genuine people that are invested in the project. 

### Top 10/20 Holders

Checks % holdings of top 10/20 wallets. Whales or wallets with a high holdings could indicate a rug pull or the ability to kill upwards momentum by selling off a large portion of tokens. 

### Holders Exceeding 6%

Again, whales are risky. 5/6% of a token is okay to hold but contracts with wallets with more than this should be looked at with caution.

### Distribution

Mass sell bots are a big problem as it cannot be detected by a simple top 10/20 percentage holdings. They can sell all of their tokens instantly, rugging the contract. They do this by spreading out all of their holdings throughout 10-100 wallets, making the holdings look okay, and all selling at the same time. This checks for suspicious distribution among these wallets.

## Devwallet

This part of the program checks aspects of the developer / creator wallet for any suspicious activity.

### Developer SOL Balance

Developers with a very high SOL balance should be a huge red flag. They more often than not, have gained this balance from malicious and fraudulent contracts.

### Developer token holdings

This checks to see what the developer is holding. CTO's of tokens exist, but generally (especially in the case of newly released tokens) if the developer has sold, they have given up on the project and this will discourage others from investing.

### Airdrops / Bundle Sniping

## Airdrops

Airdrops are simply tokens that have been transferred without being paid for through Raydium (pump.fun tokens are excluded. As this is how pump.fun works). Contracts with high numbers of airdrops are likely where the developer has minted tokens and transferred them to their other wallets or friends wallets. Should be avoided.

## Bundle Snipe

This is where someone has sniped the liquidity pool and potentially still holding the tokens from this snipe. This is usually done by a dev. Another big sign of a rug.