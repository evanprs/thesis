\version "2.18.2"
\pointAndClickOff
\header {
  title = Results
}
\score
  {
  <<
  \new Staff = "up" {
    s4 s4 s4 s4 s4 s4 s4 ees'^\markup { 27 } f'_\markup { -13 } g'_\markup { -31 } bes'_\markup { -28 } b'^\markup { 15 } des''^\markup { 16 } e''^\markup { 6 } g''_\markup { -12 } aes''_\markup { -15 } a''_\markup { -41 } bes''_\markup { -46 } bes''^\markup { 7 } 
  }
  \new Staff = "down" {
    \clef bass {
      e,,_\markup { -4 } b,,^\markup { 4 } ees,^\markup { 44 } des^\markup { 15 } d_\markup { -2 } a^\markup { 49 } bes^\markup { 17 } s4 s4 s4 s4 s4 s4 s4 s4 s4 s4 s4 s4 
    }
  }
  >>
  \header {
    piece = "All Notes"
  }
}
\score
  {
  <<
  \new Staff = "up" {
    s1 e''4^\markup { 6 } \bar "|."
e''1^\markup { 6 } s4 \bar "|."

  }
  \new Staff = "down" {
    \clef bass {
      e,,1_\markup { -4 } s4 \bar "|."
s1 e,,4_\markup { -4 } \bar "|."

    }
  }
  >>
  \header {
    piece = "Harmonics by Octave"
  }
}
\score
  {
  <<
  \new Staff = "up" {
    s1 aes''4_\markup { -15 } \bar "|."
s1 des''4^\markup { 16 } \bar "|."
s1 des''4^\markup { 16 } \bar "|."
s1 bes'4_\markup { -28 } bes''4_\markup { -46 } \bar "|."
s1 bes''4^\markup { 7 } \bar "|."
g'1_\markup { -31 } g''4_\markup { -12 } \bar "|."
bes'1_\markup { -28 } bes''4_\markup { -46 } \bar "|."
bes''1_\markup { -46 } bes''4^\markup { 7 } \bar "|."
bes''1^\markup { 7 } bes''4_\markup { -46 } \bar "|."

  }
  \new Staff = "down" {
    \clef bass {
      e,,1_\markup { -4 } s4 \bar "|."
ees,1^\markup { 44 } s4 \bar "|."
des1^\markup { 15 } s4 \bar "|."
a1^\markup { 49 } s4 s4 \bar "|."
bes1^\markup { 17 } s4 \bar "|."
s1 s4 \bar "|."
s1 s4 \bar "|."
s1 s4 \bar "|."
s1 s4 \bar "|."

    }
  }
  >>
  \header {
    piece = "Harmonics by Common Multiple"
  }
}
