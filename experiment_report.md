# Chord Representation Model

## Pitch Class Profile

A pitch class profile (PCP) of a span of music is a vector that encode the occurence fequency of the 12 pitch classes in the span. A pitch class profile $p = (f_1, f_2, \ldots, f_{12})$ where $f_i$ is the occurence frequency of pitch class $i$.

## Original Chord Detection Algorithm

The chord detection algorithm in the original paper are rootes on six pitches (C, D, E, F, G, A) and four types of "chord":

- Single
- Third
- Triad
- Seventh

The algorithm first collect the pitch profile in each bar, and uses five principles compare the pitch profile and a chord candidate to progressively eliminate candidate chords until only one candidate left.

## New Chord Detection Algorithm

The new chord detection algorithm we are using in this project is based on Fujishima's (1999) PCP matching method that find the best chord of a PCP by the maximum matching score. The matching score between PCP $p$ and a given chord $C$ is computed by doing inner product between the $p$ and the hand-crafted weight of the chord $W_C$

$$
\text{matching score}(p, C) = \sum_{i=1}^{12} f_i \times {W_C}_i
$$

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

## Effect of Chord Detection Algorithm on Query Precision

If a chord detection algorithm outputs the same chord sequence to many different melody, it could have better tolerence to user's input fault, but be bad at its primary task: indexing. To know which chord detection algorithm can give better search result, we use *average precision* to show how often is more then one melody having the same detected chord sequence. 

The precision of a query result is the number of related items divided by number of retrieved items. In this indexing senario, the number of related item is always one. So for each query result, the precision is one over number of retrieved items. And the average precision is

$$
\frac{1}{N} \sum_{i=1}^N \frac{1}{\text{\# of retrieved items when querying the i-th melody}} 
$$


## Simulation of User Input Fault


### Simulation of User Input Fault in Jianpu Representation


### Simulation of User Input Fault in Note-tuple Sequence Representation


## Configuration

We use four configurations of database: one with original chord detection algorithm, and three with our proposed algorithm with the key-chord score weight $\alpha$ being $0.0, 0.3, 1.0$. 



## Result

### Result of Query Precision

