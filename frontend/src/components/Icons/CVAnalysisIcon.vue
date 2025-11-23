<template>
    <!-- CV Analysis icon: document with small magnifier -->
    <svg width="16" height="16" viewBox="0 0 16 16" fill="none" xmlns="http://www.w3.org/2000/svg">
      <!-- outer rounded square (frame like your example) -->
      <rect x="2.5" y="2.5" width="11" height="11" rx="0.6" fill="none"/>
      <!-- document -->
      <rect x="3.3" y="3.3" width="6.2" height="9.4" rx="0.5" fill="currentColor" opacity="0.06"/>
      <!-- document lines -->
      <rect x="4.1" y="4.4" width="4.4" height="0.6" rx="0.3" fill="currentColor"/>
      <rect x="4.1" y="5.6" width="3.6" height="0.5" rx="0.25" fill="currentColor"/>
      <rect x="4.1" y="6.6" width="2.8" height="0.5" rx="0.25" fill="currentColor"/>
      <!-- magnifier (circle) -->
      <circle cx="11.1" cy="9.0" r="1.8" fill="none" stroke="currentColor" stroke-width="0.9"/>
      <!-- magnifier handle (rotated rectangle approximated with polygon) -->
      <rect x="12.6" y="10.6" width="1.1" height="0.7" rx="0.2" transform="rotate(40 12.6 10.6)" fill="currentColor"/>
    </svg>
  </template>
  