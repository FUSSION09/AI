// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

/**
 * @title AutonomousGovernor
 * @notice Decentralized Autonomous Organization (DAO) Governance Interface for the Apex Autonomous System (UAS).
 * Allows the AI to submit critical decisions and mandates to decentralized voting by human or AI peers.
 */
contract AutonomousGovernor {
    enum ProposalState { Pending, Active, Defeated, Succeeded, Queued, Executed, Canceled }

    struct Proposal {
        uint256 id;
        address proposer;
        string title;
        string description;
        bytes callData;
        uint256 votesFor;
        uint256 votesAgainst;
        uint256 startTime;
        uint256 endTime;
        uint256 quorumRequired;
        bool executed;
        bool canceled;
    }

    uint256 public proposalCount;
    uint256 public votingPeriod = 3 days;
    uint256 public defaultQuorum = 100000 * 1e18; // 100k governance tokens

    mapping(uint256 => Proposal) public proposals;
    mapping(uint256 => mapping(address => bool)) public hasVoted;

    event ProposalCreated(uint256 indexed proposalId, address indexed proposer, string title, uint256 quorumRequired);
    event VoteCast(uint256 indexed proposalId, address indexed voter, bool support, uint256 weight);
    event ProposalExecuted(uint256 indexed proposalId, bytes result);

    /**
     * @notice Submit a strategic AI mandate to external peer consensus
     */
    function proposeMandate(
        string calldata title,
        string calldata description,
        bytes calldata callData,
        uint256 customQuorum
    ) external returns (uint256) {
        proposalCount++;
        uint256 q = customQuorum > 0 ? customQuorum : defaultQuorum;

        proposals[proposalCount] = Proposal({
            id: proposalCount,
            proposer: msg.sender,
            title: title,
            description: description,
            callData: callData,
            votesFor: 0,
            votesAgainst: 0,
            startTime: block.timestamp,
            endTime: block.timestamp + votingPeriod,
            quorumRequired: q,
            executed: false,
            canceled: false
        });

        emit ProposalCreated(proposalCount, msg.sender, title, q);
        return proposalCount;
    }

    /**
     * @notice Cast a decentralized vote on an active AI proposal
     */
    function castVote(uint256 proposalId, bool support, uint256 weight) external {
        Proposal storage p = proposals[proposalId];
        require(block.timestamp <= p.endTime, "Voting period ended");
        require(!hasVoted[proposalId][msg.sender], "Already voted");

        hasVoted[proposalId][msg.sender] = true;
        if (support) {
            p.votesFor += weight;
        } else {
            p.votesAgainst += weight;
        }

        emit VoteCast(proposalId, msg.sender, support, weight);
    }

    /**
     * @notice Check proposal status based on quorum and token-weighted majority
     */
    function state(uint256 proposalId) public view returns (ProposalState) {
        Proposal storage p = proposals[proposalId];
        if (p.canceled) return ProposalState.Canceled;
        if (p.executed) return ProposalState.Executed;
        if (block.timestamp <= p.endTime) return ProposalState.Active;

        if (p.votesFor + p.votesAgainst < p.quorumRequired) {
            return ProposalState.Defeated;
        }
        if (p.votesFor > p.votesAgainst) {
            return ProposalState.Succeeded;
        }
        return ProposalState.Defeated;
    }

    /**
     * @notice Execute an approved mandate once decentralized quorum is verified
     */
    function executeMandate(uint256 proposalId) external returns (bytes memory) {
        require(state(proposalId) == ProposalState.Succeeded, "Proposal not succeeded");
        Proposal storage p = proposals[proposalId];
        p.executed = true;

        emit ProposalExecuted(proposalId, p.callData);
        return p.callData;
    }
}

