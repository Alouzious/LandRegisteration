const { ethers } = require("hardhat");

async function main() {
  const signers = await ethers.getSigners();
  console.log("Signers:", signers);

  const [deployer] = signers;
  console.log("Deploying contract with account:", deployer.address);

  // Get balance via deployer's provider in ethers v6
  const balance = await deployer.provider.getBalance(deployer.address);
  console.log("Account balance:", balance.toString());

  const LandRegistry = await ethers.getContractFactory("LandRegistry");
  const landRegistry = await LandRegistry.deploy();

  // Wait for deployment in ethers v6
  await landRegistry.waitForDeployment();

  // Get contract address in ethers v6
  console.log("LandRegistry deployed to:", await landRegistry.getAddress());
}

main()
  .then(() => process.exit(0))
  .catch(error => {
    console.error(error);
    process.exit(1);
  });
