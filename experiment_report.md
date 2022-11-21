# Implementation

## Folksong Records

A folksong record in Essen Folksong database contains following columns:

- Name of its subsection
- Title
- Source: where and how it is recorded
- Signature: An identification string of melody content
- Time unit: The time length of the unit in Jianpu format  
- Tonic: By what value the pitches of melody are normalized in Jianpu format
- Metre: The metre of the song
- Melody: Pitch normalized melody represented in Jianpu format
- Function: In which situation or purpose the tune are often used
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

The key attrbiutes of the folksong table is {Title, Signature}. We pre-process the melody into note-tuple format for computation convenience. We also create two other table for storing detected musical key and chord sequence of each folksong. 

## Implementation of Chord Detection Algorithm

To implement the chord detection function descipbed in section Method, we define a function `NoteSeqToChordSeq` that takes a pitch-normalized note sequence $\bar{x} = \bar{x}_1, \ldots \bar{x}_n$, tonic value $t$ and metre $m$, and outputs detected chord sequence $c = c_1, \ldots, c_m$. The pitch values in $\bar{x}$ will be de-normalized, thus obtain the $x$. And the moving window size and moving window step will be all set to the length of the bar  



## Content-Query Method

We implement two method to query folksong record by it content:

- By Jianpu representation
- By MusicNote sequence representation

# Experiment

## Simulation of User Input Fault


### Simulation of User Input Fault in Jianpu Representation


### Simulation of User Input Fault in Note-tuple Sequence Representation


## Result
