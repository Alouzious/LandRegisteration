
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

contract LandRegistry {
    struct LandParcel {
        string plotId;
        string ownerName;
        string district;
        string subcounty;
        string parish;
        string village;
        uint256 plotSize;
        string nationalNIN;

        address owner;
        address beneficiary;
        bool isRegistered;
        uint256 registrationDate;

        address currentTenant;
        uint256 leaseStartTime;
        uint256 leaseEndTime;
        bool isLeased;
    }

    mapping(string => LandParcel) public landParcels;
    mapping(address => string[]) public ownerToPlots;
    string[] public allPlotIds;

    address public contractOwner;

    event LandRegistered(string indexed plotId, address indexed owner, uint256 timestamp);
    event LandTransferred(string indexed plotId, address indexed oldOwner, address indexed newOwner, uint256 timestamp);
    event LandLeased(string indexed plotId, address indexed tenant, uint256 leaseStart, uint256 leaseEnd);
    event LeaseEnded(string indexed plotId, address indexed tenant, uint256 timestamp);
    event LandSplit(string indexed originalPlotId, string indexed newPlotId, address indexed newOwner, uint256 newSize);

    modifier onlyContractOwner() {
        require(msg.sender == contractOwner, "Only contract owner");
        _;
    }

    modifier onlyLandOwner(string memory plotId) {
        require(landParcels[plotId].isRegistered, "Land not registered");
        require(landParcels[plotId].owner == msg.sender, "Not land owner");
        _;
    }

    modifier validAddress(address addr) {
        require(addr != address(0), "Invalid address");
        _;
    }

    constructor() {
        contractOwner = msg.sender;
    }

    function registerLand(
        string memory plotId,
        string memory ownerName,
        string memory district,
        string memory subcounty,
        string memory parish,
        string memory village,
        uint256 plotSize,
        string memory nationalNIN
    ) public payable {
        require(bytes(plotId).length > 0, "Plot ID is required");
        require(!landParcels[plotId].isRegistered, "Already registered");
        require(msg.value >= 0.01 ether, "Registration fee is 0.01 ETH");

        landParcels[plotId] = LandParcel({
            plotId: plotId,
            ownerName: ownerName,
            district: district,
            subcounty: subcounty,
            parish: parish,
            village: village,
            plotSize: plotSize,
            nationalNIN: nationalNIN,
            owner: msg.sender,
            beneficiary: address(0),
            isRegistered: true,
            registrationDate: block.timestamp,
            currentTenant: address(0),
            leaseStartTime: 0,
            leaseEndTime: 0,
            isLeased: false
        });

        ownerToPlots[msg.sender].push(plotId);
        allPlotIds.push(plotId);

        emit LandRegistered(plotId, msg.sender, block.timestamp);
    }

    function transferLand(
        string memory plotId,
        string memory newOwnerName,
        string memory newNationalNIN,
        address newOwner
    ) public onlyLandOwner(plotId) validAddress(newOwner) {
        LandParcel storage land = landParcels[plotId];
        address oldOwner = land.owner;

        land.owner = newOwner;
        land.ownerName = newOwnerName;
        land.nationalNIN = newNationalNIN;

        _removePlotFromOwner(oldOwner, plotId);
        ownerToPlots[newOwner].push(plotId);

        emit LandTransferred(plotId, oldOwner, newOwner, block.timestamp);
    }

    function startLease(
        string memory plotId,
        address tenant,
        uint256 leaseStart,
        uint256 leaseEnd
    ) public onlyLandOwner(plotId) validAddress(tenant) {
        require(leaseStart < leaseEnd, "Invalid lease time");
        LandParcel storage land = landParcels[plotId];
        require(!land.isLeased, "Already leased");

        land.currentTenant = tenant;
        land.leaseStartTime = leaseStart;
        land.leaseEndTime = leaseEnd;
        land.isLeased = true;

        emit LandLeased(plotId, tenant, leaseStart, leaseEnd);
    }

    function endLease(string memory plotId) public onlyLandOwner(plotId) {
        LandParcel storage land = landParcels[plotId];
        require(land.isLeased, "Not leased");

        address tenant = land.currentTenant;

        land.currentTenant = address(0);
        land.leaseStartTime = 0;
        land.leaseEndTime = 0;
        land.isLeased = false;

        emit LeaseEnded(plotId, tenant, block.timestamp);
    }

    function splitAndTransferLand(
        string memory originalPlotId,
        string memory newPlotId,
        string memory newOwnerName,
        string memory newNationalNIN,
        address newOwner,
        uint256 splitPlotSize
    ) public onlyLandOwner(originalPlotId) validAddress(newOwner) {
        require(!landParcels[newPlotId].isRegistered, "New ID exists");

        LandParcel storage original = landParcels[originalPlotId];
        require(splitPlotSize > 0 && splitPlotSize < original.plotSize, "Invalid split size");

        original.plotSize -= splitPlotSize;

        landParcels[newPlotId] = LandParcel({
            plotId: newPlotId,
            ownerName: newOwnerName,
            district: original.district,
            subcounty: original.subcounty,
            parish: original.parish,
            village: original.village,
            plotSize: splitPlotSize,
            nationalNIN: newNationalNIN,
            owner: newOwner,
            beneficiary: address(0),
            isRegistered: true,
            registrationDate: block.timestamp,
            currentTenant: address(0),
            leaseStartTime: 0,
            leaseEndTime: 0,
            isLeased: false
        });

        ownerToPlots[newOwner].push(newPlotId);
        allPlotIds.push(newPlotId);

        emit LandRegistered(newPlotId, newOwner, block.timestamp);
        emit LandSplit(originalPlotId, newPlotId, newOwner, splitPlotSize);
    }

    function _removePlotFromOwner(address owner, string memory plotId) internal {
        string[] storage plots = ownerToPlots[owner];
        for (uint i = 0; i < plots.length; i++) {
            if (keccak256(bytes(plots[i])) == keccak256(bytes(plotId))) {
                plots[i] = plots[plots.length - 1];
                plots.pop();
                break;
            }
        }
    }

    function viewLandByPlotId(string memory plotId) public view returns (
        string memory, string memory, string memory, string memory, string memory,
        string memory, uint256, string memory, address, bool, uint256, address, uint256, uint256, bool
    ) {
        require(landParcels[plotId].isRegistered, "Land not found");
        LandParcel memory l = landParcels[plotId];
        return (
            l.plotId, l.ownerName, l.district, l.subcounty, l.parish,
            l.village, l.plotSize, l.nationalNIN, l.owner, l.isRegistered,
            l.registrationDate, l.currentTenant, l.leaseStartTime, l.leaseEndTime, l.isLeased
        );
    }

    function searchLandsByOwnerName(string memory name) public view returns (string[] memory) {
        uint count = 0;
        for (uint i = 0; i < allPlotIds.length; i++) {
            if (keccak256(bytes(landParcels[allPlotIds[i]].ownerName)) == keccak256(bytes(name))) {
                count++;
            }
        }

        string[] memory results = new string[](count);
        uint j = 0;
        for (uint i = 0; i < allPlotIds.length; i++) {
            if (keccak256(bytes(landParcels[allPlotIds[i]].ownerName)) == keccak256(bytes(name))) {
                results[j] = allPlotIds[i];
                j++;
            }
        }
        return results;
    }

    function withdraw() public onlyContractOwner {
        payable(contractOwner).transfer(address(this).balance);
    }
}
