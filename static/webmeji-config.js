// ✰ webmeji ✰
// little creatures that walk around your website =w=b
// inspired by shimeji, originally by Lars de Rooij
// not affiliated with any other shimeji projects
// last updated: 27 january 2026
// homepage: webmeji.neocities.org
//
// this file defines:
// - which webmeji spawn
// - which actions are allowed
// - what animations they have
// - how often actions occur

// spawning setup --------------------------------------------------
// define which creatures spawn on the page. remove any unwanted ones.
// each id must be unique
// if two of them overlap and pet and dragging interactions happen, only the one stated here last will get interacted with
window.SPAWNING = [
  { id: 'webmeji-0', config: 'MIKU_CONFIG' }
];

// base shimeji config ----------------------------------------------
// all configs should have same actions, but allowances can differ
window.SHIMEJI_CONFIG = {
  // pet   = hover animation (hard to see on mobile)
  // drag  = click or touch to pick up
  // top / left / right allow edge interactions
  // remove whichever you don't want, the only exceptions is that bottom must always be enabled
  ALLOWANCES: ['pet', 'drag', 'bottom', 'top', 'left', 'right'],

  // movement and physics -------------------------------------------
  // values are pixels movements per frame
  walkspeed: 50,
  fallspeed: 200,
  jumpspeed: 150,

  // time in ms before standing back up after falling
  gettingupspeed: 2000,

  // common idle and movement animations on the bottom edge ---------
  // these are the most frequently used actions
  // interval = time between frames (ms)
  // loops = how many times the frame sequence repeats
  // randomizeDuration sets random timeframe for actions, tune min and max to desired length
  walk: {
    frames: ["/static/shimeji/shime1.png", "/static/shimeji/shime2.png", "/static/shimeji/shime3.png", "/static/shimeji/shime2.png"],
    interval: 175, loops: 6},

  stand: {
    frames: ["/static/shimeji/shime1.png"],
    interval: 200, loops: 1},

  sit: {
    frames: ["/static/shimeji/shime11.png"],
    interval: 1000, loops: 1,
    randomizeDuration: true, min: 3000, max: 11000},

  spin: {
    frames: ["/static/shimeji/shime1.png"],
    interval: 150, loops: 3},

  dance: {
    frames: ["/static/shimeji/shime5.png", "/static/shimeji/shime6.png", "/static/shimeji/shime1.png"],
    interval: 200, loops: 5},

  trip: {
    frames: ["/static/shimeji/shime20.png", "/static/shimeji/shime21.png", "/static/shimeji/shime21.png", "/static/shimeji/shime20.png", "/static/shimeji/shime21.png", "/static/shimeji/shime21.png"],
    interval: 250, loops: 1},

  // behavior flow control ------------------------------------------
  // prevents awkward transitions like dancing immediately after sitting
  forcewalk: { // uses the walking frames, by default happens after tripping and spinning
    loops: 6},

  forcethink: { // by default happens after dancing
    frames: ["/static/shimeji/shime27.png", "/static/shimeji/shime28.png"],
    interval: 500, loops: 2},

  // user interaction animations ------------------------------------
  pet: {
    frames: ["/static/shimeji/shime15.png", "/static/shimeji/shime16.png", "/static/shimeji/shime17.png"],
    interval: 75},

  drag: {
    frames: ["/static/shimeji/shime5.png", "/static/shimeji/shime7.png", "/static/shimeji/shime5.png", "/static/shimeji/shime6.png", "/static/shimeji/shime8.png", "/static/shimeji/shime6.png"],
    interval: 210},

  // falling and recovery animations --------------------------------
  falling: {
    frames: ["/static/shimeji/shime4.png"],
    interval: 200, loops: 2},

  fallen: {
    frames: ["/static/shimeji/shime19.png", "/static/shimeji/shime18.png"],
    interval: 250, loops: 1},

  // action frequency and decision logic ----------------------------
  // anytime an action needs to be chosen, it randomly picks one of these
  // thus, having an action in here more than others, makes it happen more
  ORIGINAL_ACTIONS: [
    'walk','walk','walk','walk','walk','walk',
    'walk','walk','walk','walk','walk','walk',
    'spin','spin','spin',
    'sit','sit',
    'dance','dance',
    'trip'
  ],

  EDGE_ACTIONS: [
    'hang','hang',
    'climb','climb','climb','climb',
    'fall','fall'
  ],

  // when chosing an action on the bottom, it has this change to jump to an edge (if allowed)
  // this is standalone from the other action select
  JUMP_CHANCE: 0.05, // below 0 = never jump; above 1 = jump almost always

  // edge-specific animations ---------------------------------------
  climbSide: {
    frames: ["/static/shimeji/shime13.png", "/static/shimeji/shime14.png"],
    interval: 200, loops: 2},

  hangstillSide: {
    frames: ["/static/shimeji/shime12.png"],
    interval: 200, loops: 2,
    randomizeDuration: true, min: 3000, max: 11000},

  climbTop: {
    frames: ["/static/shimeji/shime24.png", "/static/shimeji/shime25.png"],
    interval: 200, loops: 6},

  hangstillTop: {
    frames: ["/static/shimeji/shime23.png"],
    interval: 200, loops: 2,
    randomizeDuration: true, min: 3000, max: 11000},

  jump: {
    frames: ["/static/shimeji/shime22.png"],
    interval: 200}
};


// second config ----------------------------------------------------

window.MIKU_CONFIG = {
  // pet   = hover animation (hard to see on mobile)
  // drag  = click or touch to pick up
  // top / left / right allow edge interactions
  // remove whichever you don't want, the only exceptions is that bottom must always be enabled
  ALLOWANCES: ['pet', 'drag', 'bottom', 'top', 'left', 'right'],

  // movement and physics -------------------------------------------
  // values are pixels movements per frame
  walkspeed: 50,
  fallspeed: 150,
  jumpspeed: 200,

  // time in ms before standing back up after falling
  gettingupspeed: 3500,

  // common idle and movement animations on the bottom edge ---------
  // these are the most frequently used actions
  // interval = time between frames (ms)
  // loops = how many times the frame sequence repeats
  // randomizeDuration sets random timeframe for actions, tune min and max to desired length
  walk: {
    frames: ["/static/miku/shime1.png", "/static/miku/shime2.png", "/static/miku/shime3.png", "/static/miku/shime2.png"], 
    interval: 175, loops: 6},

  stand: {
    frames: ["/static/miku/shime1.png"], 
    interval: 1000, loops: 1},

  sit: {
    frames: ["/static/miku/shime11.png"], 
    interval: 1000, loops: 1,
    randomizeDuration: true, min: 3000, max: 11000},

  spin: {
    frames: ["/static/miku/shime1.png"], 
    interval: 150, loops: 3},

  dance: {
    frames: ["/static/miku/shime5.png", "/static/miku/shime6.png", "/static/miku/shime1.png"], 
    interval: 200, loops: 2},

  trip: {
    frames: ["/static/miku/shime18.png", "/static/miku/shime19.png", "/static/miku/shime19.png"], 
    interval: 250, loops: 1},

  // behavior flow control ------------------------------------------
  // prevents awkward transitions like dancing immediately after sitting
  forcewalk: { // uses the walking frames
    loops: 6},

  forcethink: {
    frames: ["/static/miku/shime27.png", "/static/miku/shime28.png"], 
    interval: 500, loops: 2},

  // user interaction animations ------------------------------------
  pet: {
    frames: ["/static/miku/shime15.png", "/static/miku/shime16.png", "/static/miku/shime17.png"], 
    interval: 400},

  drag: {
    frames: ["/static/miku/shime7.png", "/static/miku/shime5.png", "/static/miku/shime8.png", "/static/miku/shime6.png"], 
    interval: 210},

  // falling and recovery animations --------------------------------
  falling: {
    frames: ["/static/miku/shime10.png", "/static/miku/shime18.png"], 
    interval: 200, loops: 2},

  fallen: {
    frames: ["/static/miku/shime9.png", "/static/miku/shime4.png", "/static/miku/shime19.png"], 
    interval: 250, loops: 1},

  // action frequency and decision logic ----------------------------
  // anytime an action needs to be chosen, it randomly picks one of these
  // thus, having an action in here more than others, makes it happen more
  ORIGINAL_ACTIONS: [
    'walk','walk','walk','walk','walk','walk',
    'spin','spin','spin',
    'sit','sit',
    'dance','dance','dance','dance','dance',
    'trip'
  ],

  EDGE_ACTIONS: [
    'hang','hang',
    'climb','climb','climb','climb','climb',
    'fall'
  ],

  // when chosing an action on the bottom, it has this change to jump to an edge (if allowed)
  // this is standalone from the other action select
  JUMP_CHANCE: 0.1, // below 0 = never jump; above 1 = jump almost always

  // edge-specific animations ---------------------------------------
  climbSide: {
    frames: ["/static/miku/shime13.png", "/static/miku/shime14.png"], 
    interval: 200, loops: 2},

  hangstillSide: {
    frames: ["/static/miku/shime12.png"], 
    interval: 200, loops: 2,
    randomizeDuration: true, min: 3000, max: 11000},

  climbTop: {
    frames: ["/static/miku/shime24.png", "/static/miku/shime25.png"], 
    interval: 200, loops: 8},

  hangstillTop: {
    frames: ["/static/miku/shime23.png"], 
    interval: 200, loops: 2,
    randomizeDuration: true, min: 3000, max: 11000},

  jump: {
    frames: ["/static/miku/shime22.png"], 
    interval: 200}
};
