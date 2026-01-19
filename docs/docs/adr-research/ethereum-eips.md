# Ethereum EIPs - Ethereum Improvement Proposals

## Overview

EIPs (Ethereum Improvement Proposals) are the standardization and documentation process for improvements to the Ethereum blockchain platform. They represent one of the most rigorous and well-established decision documentation processes in the blockchain space.

**Repository**: https://github.com/ethereum/EIPs **Documentation**: Approximately 870 EIP documents **Purpose**: "To standardize and provide high-quality documentation for Ethereum itself and conventions built upon it"

## EIP Categories

The system divides proposals into six main types:

### 1. Core EIPs

Changes to the Ethereum consensus protocol:

- Consensus rules
- Blockchain validation
- Proof-of-work/proof-of-stake mechanisms
- Fork implementations
- Critical protocol updates

**Impact**: Requires all nodes to upgrade **Examples**: Major network upgrades (Shanghai, Merge, etc.)

### 2. Networking EIPs

Peer-to-peer network layer specifications:

- Network protocols
- Node communication
- Devp2p improvements
- Discovery mechanisms

**Impact**: Affects node communication **Examples**: Network optimization proposals

### 3. Interface EIPs

Standards determining user and application interaction with blockchain:

- JSON-RPC specifications
- API standards
- Client interfaces
- Developer tools

**Impact**: Affects how applications interact with Ethereum **Examples**: RPC method specifications

### 4. Meta EIPs

Miscellaneous improvements requiring consensus:

- Process improvements
- Guidelines
- Decision-making procedures
- EIP process itself (EIP-1)

**Impact**: Affects Ethereum development process **Examples**: EIP-1 (EIP Purpose and Guidelines)

### 5. Informational EIPs

Non-binding documentation:

- Design rationale
- General guidelines
- Best practices
- Educational content

**Impact**: Informational only, no implementation required **Examples**: Design philosophy documents

### 6. ERCs (Ethereum Request for Comments)

Application layer standards - **now in separate repository**:

- Token standards (ERC-20, ERC-721, ERC-1155)
- Smart contract patterns
- Application conventions

**Important**: ERCs are now maintained at https://github.com/ethereum/ercs

## EIP Process

### Before Proposing

According to the README:

> "Ideas MUST be thoroughly discussed on Ethereum Magicians or Ethereum Research"

This ensures:

- Community vetting before formal submission
- Refinement of ideas
- Identification of issues
- Building consensus

### Proposal Lifecycle

1. **Discussion**: Informal discussion on forums
1. **Draft**: Initial EIP written using template
1. **Review**: Community and editors review
1. **Last Call**: Final comment period
1. **Final**: Accepted and finalized
1. **Living**: For documents that are continually updated
1. **Stagnant**: Inactive for 6+ months
1. **Withdrawn**: Author withdrew proposal
1. **Rejected**: Not accepted

### EIP-1: The Meta-EIP

EIP-1 governs the entire publication process and is required reading for anyone proposing an EIP. It defines:

- EIP formats and structures
- Review processes
- Status transitions
- Editor responsibilities
- Quality standards

## EIP Structure

### Required Components

Based on typical EIP structure:

**Header/Metadata**

- EIP number
- Title
- Author(s)
- Status
- Type
- Category
- Created date
- Requires (dependencies)
- Replaces/Superseded-By

**Abstract**

Brief technical summary (~200 words)

**Motivation**

Why the EIP is necessary, what problem it solves

**Specification**

Technical details of the proposal:

- Precise technical description
- Formal specifications
- Implementation details
- Edge cases

**Rationale**

Design decisions and alternatives considered:

- Why this approach?
- What alternatives were considered?
- What trade-offs were made?

**Backwards Compatibility**

Impact on existing implementations:

- Breaking changes
- Migration requirements
- Deprecated features

**Test Cases** (for Core EIPs)

Comprehensive test coverage

**Reference Implementation**

Working code demonstrating the proposal

**Security Considerations**

Security implications and risks

## Technical Rigor

### High Standards

EIPs require:

- **Precise specification**: Implementable from document alone
- **Technical completeness**: All edge cases covered
- **Test cases**: Comprehensive validation
- **Reference implementation**: Proof of concept
- **Security analysis**: Threat model considered

### Editor Review

Designated EIP editors:

- Review for technical quality
- Ensure format compliance
- Check for completeness
- Assign EIP numbers
- Manage status transitions

## Community Governance

### Decentralized Decision Making

- No single authority approves EIPs
- Consensus through discussion
- Multiple stakeholder types (developers, miners, users)
- Transparent process

### Stakeholder Groups

- **Core developers**: Protocol implementation
- **Client teams**: Node software
- **Application developers**: Smart contracts and dApps
- **Users**: Token holders and network participants
- **Researchers**: Academic and theoretical input

## Integration with Development

### Fork Coordination

Major Ethereum upgrades bundle multiple EIPs:

- **Shanghai**: Multiple EIPs implemented together
- **The Merge**: Transition to proof-of-stake
- **London**: EIP-1559 and others

This requires:

- Dependency management
- Testing across EIPs
- Coordinated deployment
- Network-wide upgrade

### Implementation Tracking

- Multiple client implementations (Geth, Besu, Nethermind, etc.)
- Each must implement EIPs independently
- Cross-client testing required
- Testnet deployment before mainnet

## Documentation System

### Static Site

- Built with Jekyll (Ruby 3.1.4)
- GitHub Pages deployment
- RSS feeds for updates
- Categorized browsing
- Search functionality

### Organization

- Individual markdown files per EIP
- Consistent naming: `eip-NNNN.md`
- Template for new proposals
- Configuration for site generation

## Benefits of EIP Process

### For the Network

- **Standardization**: Consistent improvements
- **Quality**: High technical bar
- **Security**: Thorough review
- **Compatibility**: Coordinated changes

### For Developers

- **Clarity**: Clear specifications
- **Reference**: Test cases and implementations
- **History**: Understanding of design evolution
- **Standards**: Common patterns and practices

### For the Ecosystem

- **Transparency**: Open proposal process
- **Participation**: Anyone can propose
- **Governance**: Decentralized decision making
- **Documentation**: Permanent record

## Challenges

### High Barrier to Entry

- Requires significant technical expertise
- Formal writing style
- Comprehensive specification
- Reference implementation

### Long Process

- Multiple review stages
- Community consensus building
- Cross-client implementation
- Testing and deployment

### Coordination Complexity

- Multiple independent teams
- Global distributed contributors
- Network upgrade coordination
- Backward compatibility maintenance

## Comparison to Software ADRs

### Similarities

- Document important decisions
- Capture rationale
- Permanent record
- Version controlled

### Differences

| Aspect               | EIPs                       | Traditional ADRs            |
| -------------------- | -------------------------- | --------------------------- |
| **Scope**            | Network-wide protocol      | Single project/application  |
| **Stakeholders**     | Entire ecosystem           | Internal team               |
| **Process**          | Highly formal, multi-stage | Lightweight, team consensus |
| **Technical Detail** | Exhaustive specification   | Contextual detail as needed |
| **Review**           | Public, multiple reviewers | Team review                 |
| **Implementation**   | Multiple independent teams | Single team                 |
| **Time Scale**       | Months to years            | Days to weeks               |

## Use Cases for EIP-style Process

### Best For

- **Protocol development**: Network-wide standards
- **Public blockchains**: Decentralized governance
- **Open standards**: Industry-wide adoption
- **Critical infrastructure**: High-stakes decisions
- **Multiple implementations**: Interoperability required

### Overkill For

- **Internal applications**: Single team/codebase
- **Rapid iteration**: Fast-moving projects
- **Small changes**: Minor improvements
- **Proprietary systems**: No external stakeholders

## Key Takeaways

1. **Most rigorous process**: Highest bar for quality and completeness
1. **Community-driven**: Open participation and governance
1. **Protocol-level**: For network-wide changes
1. **Long timelines**: Thorough but slow
1. **Multiple implementations**: Requires precise specification
1. **Permanent record**: Comprehensive historical documentation

## Applicable Lessons for Software Projects

Even if not adopting full EIP rigor, teams can learn from:

- **Template structure**: Comprehensive sections
- **Rationale section**: Document alternatives considered
- **Security considerations**: Explicit threat analysis
- **Test cases**: Validation requirements
- **Reference implementation**: Proof of concept
- **Status tracking**: Clear lifecycle states
- **Backwards compatibility**: Impact analysis

## Use Cases

- **Best for**: Blockchain protocols and decentralized networks
- **Project Size**: Very large, network-scale projects
- **Team Size**: Multiple independent teams
- **Culture**: Open source, decentralized governance
- **Formality**: Highly formal
- **Time Investment**: Substantial (months to years per proposal)
- **Standards**: Industry-wide or ecosystem-wide standards
