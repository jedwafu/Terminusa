// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "@koii/token/KOII.sol";
import "@openzeppelin/contracts/security/ReentrancyGuard.sol";

contract SecureTACBridge is ReentrancyGuard {
    KOII public koiiToken;
    uint256 public tacPerKOII = 100;
    
    event Conversion(address indexed user, uint256 koiiIn, uint256 tacOut);
    
    constructor(address _koiiToken) {
        koiiToken = KOII(_koiiToken);
    }
    
    function convertKOIIToTAC(uint256 koiiAmount) external nonReentrant {
        require(koiiToken.transferFrom(msg.sender, address(this), koiiAmount),
            "Transfer failed");
        uint256 tacAmount = koiiAmount * tacPerKOII;
        emit Conversion(msg.sender, koiiAmount, tacAmount);
    }
}