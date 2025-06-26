require("dotenv").config();
require("@nomicfoundation/hardhat-toolbox");

const { SEPOLIA_RPC_URL, PRIVATE_KEY } = process.env;

module.exports = {
  solidity: {
    version: "0.8.19",
    settings: {
      optimizer: {
        enabled: true,
        runs: 200,
      },
      viaIR: true, // Enables via-IR to fix stack-too-deep
    },
  },
  networks: {
    sepolia: {
      url: SEPOLIA_RPC_URL || "",
      accounts: PRIVATE_KEY ? [PRIVATE_KEY] : [],
    },
    ganache: {
      url: "http://127.0.0.1:8545",
      accounts: " 0x47c99abed3324a2707c28affff1267e45918ec8c3f20b8aa892e8b065d2942dd"
    },
  },
};
