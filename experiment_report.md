# Chord Representation Model


## Chord Detection Algorithm


## PAT-Tree


# Implementation

## Folksong Records

A folksong record in Essen Folksong database contains following columns:

- Name of its subsection
- Title
- Source: where and how it is recorded
- Signature: An identification string of its melody
- Time unit: The time length of the unit in Jianpu format  
- Tonic: By what value the pitches of melody are normalized in Jianpu format
- Metre: The metre of the song
- Melody: Pitch normalized melody represented in Jianpu format
- Function: In which situation or purpose the tune is used
- Comment
- Lyrics

For simplification, we only keep the necessary columns in ours implementation. These are:

- Name of its subsection
- Title
- Signature
- Time unit
- Tonic
- Metre
- Melody (represented in Jianpu format)
- Melody (represented in note-tuple format)

The key attrbiutes of the folksong table is {Title, Signature}. We pre-process the melody from Jianpu format into note-tuple format for computation convenience. We also create two other table for storing detected musical key and chord sequence of each folksong. 

## Implementation of Chord Detection Algorithm

To implement the chord detection algorithm, we define a function `NoteSeqToChordSeq` that takes a pitch-normalized note sequence $\bar{x} = \bar{x}_1, \ldots \bar{x}_n$, tonic value $t$ and metre $m$, and outputs detected chord sequence $c = c_1, \ldots, c_m$. The pitch values in $\bar{x}$ will be de-normalized to obtain the original melody $x$. And the moving window size and moving window step will be all set to the length of one bar.  

## Content-Query Method

We implement a query method that support two different melody representation: Jianpu and note-tuple. 

# Experiment

## Effectiveness of Key-Chord Matching Score

We use average precision to evaluate how often is more then one melody having the same detected chord sequence. The precision of a retrieval is the number of related items divided by number of retrieved items. In the indexing senario, the number of related item is always one. So for each retrieval, the precision is one over number of retrieved items.

$$
\frac{1}{N} \sum_{i=1}^N \frac{1}{\text{\# of retrieved items}} 
$$



## Simulation of User Input Fault


### Simulation of User Input Fault in Jianpu Representation


### Simulation of User Input Fault in Note-tuple Sequence Representation


## Result
