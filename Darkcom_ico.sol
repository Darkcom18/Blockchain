pragma solidity ^0.5.1;

contract darkcom_ico{
    // Max supply
    uint public max_darkcomcoin = 1000000000;
    // Convert rate for darkcom_ico
    uint public usd_to_darkcomcoin = 1;
    // Total number sales to investor
    uint public total_darkcomcoin_sale = 0; // At begining noone can buy.
    // Mapping from investors address to ico equity
    mapping(address => uint) equity_darkcomcoin;
    mapping(address => uint) equity_usd;
    // Check whether investors can buy coin 
    modifier can_buy_darkcomcoin(uint usd_invested){
        require(usd_invested * usd_to_darkcomcoin*total_darkcomcoin_sale < max_darkcomcoin );
        _;
    }
    // Getting the equtiy of darkcomcoin in investors
    function equity_in_darkcomcoin(address investor) external view returns (uint){
        return equity_darkcomcoin[investor];
        
    }
    // Getting the equity of USD in investors
    function equity_in_usd(address investor) external view returns (uint){
        return equity_usd[investor];
    }
    //Buy Darkcom coin
    function buy_darkcomcoin(address investor,uint usd_invested) external
    can_buy_darkcomcoin(usd_invested){
        uint darkcomcoin_bought = usd_invested * usd_to_darkcomcoin;
        equity_darkcomcoin[investor] += darkcomcoin_bought;
        equity_usd[investor] = equity_darkcomcoin[investor]/usd_to_darkcomcoin;
        total_darkcomcoin_sale += darkcomcoin_bought;
    }
    //Sell darkcomcoin
    function sell_darkcomcoin(address investor,uint darkcomcoin_sold) external{
        equity_darkcomcoin[investor] -= darkcomcoin_sold;
        equity_usd[investor] = equity_darkcomcoin[investor]/usd_to_darkcomcoin;
        total_darkcomcoin_sale -= darkcomcoin_sold;
    }
}
