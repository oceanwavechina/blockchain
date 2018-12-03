#  toyblockchain
 
敲的这个大神的例子，稍有修改，意在动手写一个blockchain，以便直观的了解 blockchain的例子

[Learn Blockchains by Building One](https://hackernoon.com/learn-blockchains-by-building-one-117428612f46)

###  结合bitcoin白皮书的步骤 【Bitcoin: A Peer-to-Peer Electronic Cash System】
    The steps to run the network are as follows: 
    1. New transactions are broadcast to all nodes.
    2. Each node collects new transactions into a block.  
    3. Each node works on finding a difficult proof-of-work for its block.
    4. When a node finds a proof-of-work, it broadcasts the block to all nodes.
    5. Nodes accept the block only if all transactions in it are valid and not already spent.
    6. Nodes express their acceptance of the block by working on creating the next block in the chain, using the hash of the accepted block as the previous hash.
    
    每个节点，通过通过产生一个新的block来，进行交易操作，也就是把自己想要完成的交易追加到这个新的block上。
    每次产生一个新的block的时候，都要完成 proof-of-work, 而proof-of-work也是要引用上一次的proof来计算的，然后在追加到chain上




### 几个问题
    
    1. 每个节点都要存储所有的block吗，随着时间拉长，chain会无限增长
    2. 是不是每个新节点加入都有进行resolve
    3. 如果没有交集的两个node在进行resolve的时候，有一方的信息不就丢了么
        * 这个不用担心，因为是在统一系统，必定是哟交集的，因为源头必然是一个
    4. 如果A向B进行了一次交易，在B没有产生新的block来确认此向交易时，其他node已经领先计算出了下一node，那A向B的这次交易不就没办法确认了吗，如果B的机器的计算能力及其差，是不是意味着它永远接不上chain了？懵逼。。。。

### 其他
    所以，只是说原理是这样的，bitcoin的具体实现细节??

