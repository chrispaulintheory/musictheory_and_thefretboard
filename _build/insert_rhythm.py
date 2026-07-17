#!/usr/bin/env python3
"""One-off: insert the two Rhythm chapters at the END of Part I (Basic Concepts)
as chapters 7 & 8, and renumber all later chapters (+2). Idempotent."""
from pathlib import Path

SRC = Path(__file__).parent.parent / "Music-Theory-and-The-Fretboard-Level-1-1709264790.-htmlbook.html"
text = SRC.read_text(encoding="utf-8")

if 'id="chapter-rhythm-beat-measures-note-durations"' in text:
    print("Rhythm chapters already present — nothing to do.")
    raise SystemExit(0)

# ── 1. Renumber chapter-number subtitles 7..47 -> +2 (high to low) ────────────
for n in range(47, 6, -1):
    text = text.replace(
        f'class="chapter-number">{n}</p>',
        f'class="chapter-number">{n + 2}</p>',
    )

# ── 2. Renumber "Chapter NN." references in the bonus part-intro lists ────────
for n in range(47, 6, -1):
    text = text.replace(f"Chapter {n}.", f"Chapter {n + 2}.")

# ── 3. The two Rhythm chapter sections (numbered 7 & 8) ───────────────────────
RHYTHM = r'''    <section data-type="chapter" class="chapter" id="chapter-rhythm-beat-measures-note-durations" title="Rhythm: The Beat, Measures, and Note Durations">
         <header>
              <h1 class="chapter-title">Rhythm: The Beat, Measures, and Note Durations</h1>
              <p data-type="subtitle" class="chapter-number">7</p>
         </header>
         <p>Alongside pitch and notes, there is a third basic idea every musician needs: <strong>rhythm</strong>&#8212;<em>when</em> the notes happen and how long they last. You already feel rhythm in your body whenever you tap your foot to a song. These next two chapters give names to what your foot is doing. (We will use rhythm constantly once we start playing chords and scales later in the book.)</p>
         <h4 style="text-align: center">The beat = the pulse of the song</h4>
         <p>The beat is the steady, even pulse you naturally tap your foot to. Watch your foot: it goes <strong>down</strong>, then <strong>up</strong>, then down, then up&#8212;a simple, repeating motion. That down-and-up of the foot is going to help us count every rhythm in these chapters, so get comfortable with it now.</p>
         <h4 style="text-align: center">The quarter note = one beat</h4>
         <p>In music we have a way to write down just one beat, and it is called the <strong>quarter note</strong>. A quarter note lasts exactly one beat. Every quarter note has two parts: the <strong>note head</strong> (the circle) and the <strong>stem</strong> (the line coming off it).</p>
         <p>In standard notation a quarter note is a filled-in note head with a stem. In <strong>guitar tab</strong>, instead of a note head we write the <strong>fret number</strong>, and a stem comes down from it to show the rhythm. (If you use a program like Songsterr, a quarter note shows up as a fret number with a short line extending down from it.)</p>
         <p>If you write eight quarter notes in a row, you count them out loud as you tap: &#8220;1, 2, 3, 4, 5, 6, 7, 8.&#8221; Try it&#8212;put on a simple drum beat, and tap your foot once on every quarter note.</p>
         <h4 style="text-align: center">Measures and bar lines</h4>
         <p>Counting &#8220;1, 2, 3, 4, 5, 6, 7, 8&#8230;&#8221; gets unwieldy fast, so we organize music into small chunks. We draw a vertical line through the staff called a <strong>bar line</strong>. The space between two bar lines is called a <strong>measure</strong> (also called a bar).</p>
         <p>Here is the important part: when you reach a bar line, you do <em>not</em> keep counting upward. You start over at &#8220;1.&#8221; So eight quarter notes split into two measures are counted &#8220;1, 2, 3, 4 &#8230; 1, 2, 3, 4&#8221; instead of &#8220;1&#8230;8.&#8221; A <strong>double bar line</strong> at the very end tells you the music has finished. In tab, measures are usually numbered (1, 2, 3, 4&#8230;) so you can keep track of where you are.</p>
         <h4 style="text-align: center">The time signature</h4>
         <p>At the very start of a piece you will see two numbers stacked on top of each other. This is the <strong>time signature</strong>, and it tells you how the song&#8217;s rhythm is organized.</p>
         <p><strong>The top number</strong> tells you <em>how many beats</em> are in each measure. A 4 on top means four beats per measure; a 3 on top means three beats per measure; a 5 would mean five.</p>
         <p><strong>The bottom number</strong> tells you <em>what kind of note gets one beat</em>. Here is a trick: read the time signature as if it were a fraction. The signature 4/4 reads as &#8220;four-fourths.&#8221; Another word for a &#8220;fourth&#8221; is a <em>quarter</em>&#8212;so the bottom 4 is telling you the <strong>quarter note</strong> gets one beat. Put it together and 4/4 means: four beats in each measure, and the quarter note gets the beat. This is the most common time signature in popular music.</p>
         <h4 style="text-align: center">The half note = two beats</h4>
         <p>Now let&#8217;s build longer notes. If you combine two quarter notes into a single note, how many beats is it? Two (1 + 1 = 2). That new note is the <strong>half note</strong>. Its note head is <em>empty</em> (not filled in) and it has a stem. You count it across its full length: &#8220;1&#8211;2&#8221; or &#8220;3&#8211;4.&#8221; In tab, a half note often appears as a fret number inside a small circle with a half-length stem.</p>
         <h4 style="text-align: center">The whole note = four beats</h4>
         <p>Combine two half notes and you get the <strong>whole note</strong>: four beats long. It is drawn as just a circle with <em>no</em> stem. In 4/4 time a whole note &#8220;takes up the whole measure&#8221;&#8212;you strike it once and let it ring for all four beats while your foot keeps tapping &#8220;1, 2, 3, 4.&#8221;</p>
         <p>That is the core toolkit: the beat, the quarter note (1 beat), the half note (2 beats), and the whole note (4 beats), all organized into measures by a time signature. In the next chapter we add silence, faster notes, and a couple of ways to stretch a note&#8217;s value.</p>
    </section>
    <section data-type="chapter" class="chapter" id="chapter-rhythm-rests-eighth-notes-ties-dots" title="Rhythm: Rests, Eighth Notes, Ties, and Dots">
         <header>
              <h1 class="chapter-title">Rhythm: Rests, Eighth Notes, Ties, and Dots</h1>
              <p data-type="subtitle" class="chapter-number">8</p>
         </header>
         <p>Music is not only sound&#8212;it is also <em>silence</em> placed exactly in time. In this chapter we add rests (silence), eighth notes (faster notes), and two tools&#8212;ties and dots&#8212;for lengthening a note.</p>
         <h4 style="text-align: center">Rests = the sound of silence</h4>
         <p>A quarter note is one beat of <em>sound</em>. The opposite of sound is silence, and a <strong>rest</strong> is the symbol that tells you not to play&#8212;while the beat keeps right on going. Each note value has a matching rest:</p>
         <ul>
              <li>The <strong>quarter rest</strong> = one beat of silence.</li>
              <li>The <strong>half rest</strong> = two beats of silence. It looks like a small rectangle.</li>
              <li>The <strong>whole rest</strong> = four beats of silence. It is the same rectangle shape as the half rest.</li>
         </ul>
         <p>Because the half rest and whole rest look alike, here is how to tell them apart in tab: the <strong>half rest sits on top of the G string</strong> (the 3rd string), and the <strong>whole rest hangs down from the B string</strong> (the 2nd string). If you clap four quarter notes but the third beat is a quarter rest, you simply make no sound on beat 3&#8212;&#8220;1, 2, (rest), 4&#8221;&#8212;while your foot never stops tapping.</p>
         <h4 style="text-align: center">The eighth note = half a beat</h4>
         <p>To make a faster note, we split the quarter note in half. Since a quarter note is one beat, half of it is <strong>half a beat</strong>&#8212;so <em>two</em> eighth notes fit inside a single beat. Eighth notes have a <strong>flag</strong>, and when you write several in a row they are joined by a <strong>beam</strong>.</p>
         <p>This is where the down-and-up of your foot pays off. Count eighth notes as &#8220;<strong>1</strong> and <strong>2</strong> and <strong>3</strong> and <strong>4</strong> and.&#8221; The <em>number</em> happens when your foot is <strong>down</strong>; the <em>&#8220;and&#8221;</em> happens when your foot is <strong>up</strong>. So a full measure of eighth notes is: down-up, down-up, down-up, down-up, counted &#8220;1-and-2-and-3-and-4-and.&#8221;</p>
         <p>There is also an <strong>eighth rest</strong>&#8212;half a beat of silence&#8212;which looks like a small flag on a short stem (a little like the letter &#8220;y&#8221;). If the last half-beat of a measure is an eighth rest, you still count the &#8220;and,&#8221; you just don&#8217;t play it. We often write that silent count in parentheses, like &#8220;&#8230;4 (and).&#8221;</p>
         <h4 style="text-align: center">Ties = connecting two notes</h4>
         <p>A <strong>tie</strong> is a curved line that connects two notes. You play the first note and hold it through the value of both&#8212;you do <em>not</em> pluck the second one. For example, tying two quarter notes together gives you exactly the same sound as one half note. When counting, a tie is often shown with a hyphen, like &#8220;1&#8211;2.&#8221; Sometimes a songwriter writes a half note and sometimes two tied quarter notes&#8212;they can mean the same length; it just depends on the song.</p>
         <h4 style="text-align: center">Dots = add half the value</h4>
         <p>A <strong>dot</strong> placed after a note adds <em>half</em> of that note&#8217;s value. Think of it with plain numbers: dot a 4 and you add half of 4 (which is 2) to get 6; dot a 10 and you add 5 to get 15; dot an 80 and you add 40 to get 120.</p>
         <p>Now apply that to notes. A half note is 2 beats; a <strong>dotted half note</strong> adds half of 2 (one beat) for a total of <strong>3 beats</strong>&#8212;very handy in 3/4 time, where it fills a whole measure.</p>
         <p>A <strong>dotted quarter note</strong> is a quarter note (1 beat) plus half its value (an eighth note, half a beat), for one-and-a-half beats. It creates the rhythm counted &#8220;1, 2-and, 3, 4,&#8221; where the held note absorbs the next half-beat. In fact, a dotted quarter note sounds <em>identical</em> to a quarter note tied to an eighth note&#8212;the dot is just a tidier way to write the same idea.</p>
         <p>That is Level 1 rhythm. With the beat, measures, time signatures, the note values (whole, half, quarter, eighth) and their rests, plus ties and dots, you can read and count the rhythms behind the vast majority of popular songs&#8212;and, just as importantly, write down your own.</p>
    </section>
'''

# ── 4. Insert at the end of Part I, just before Part II opens ─────────────────
anchor = '</div>\n<div data-type="part" class="part" id="part-main-body">'
assert text.count(anchor) == 1, f"expected 1 Part I/II boundary, found {text.count(anchor)}"
text = text.replace(anchor, RHYTHM + '</div>\n<div data-type="part" class="part" id="part-main-body">', 1)

# ── 5. Add two rhythm bullets to the Part I overview list ─────────────────────
last_bullet = "<li>What are the &#8220;dots&#8221; or &#8220;dot inlays&#8221; on a guitar?</li>"
if last_bullet in text:
    text = text.replace(
        last_bullet,
        last_bullet
        + "\n         <li>The beat, measures, and time signatures.</li>"
        + "\n         <li>Note durations: how long to hold each note (and rests).</li>",
        1,
    )

SRC.write_text(text, encoding="utf-8")
print("Inserted Rhythm chapters into Part I and renumbered later chapters.")
