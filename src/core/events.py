"""
Custom pygame event type constants for game-specific input (e.g. MIDI).
"""
import pygame

# MIDI note events (posted by MidiInput when keys are pressed/released)
MIDI_NOTE_ON = pygame.USEREVENT + 1
MIDI_NOTE_OFF = pygame.USEREVENT + 2
