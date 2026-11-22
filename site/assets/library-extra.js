/* SHIVAS own photos added by hand on 22 Nov 2026, until they go through the SHIVAS image-library pipeline.
   Load this right after assets/library.js (item pages and the three division pages do). It adds the photos to
   window.SHIVAS_LIBRARY: their entries, and their places in each product's gallery (own photos before supplier
   photos). Files: assets/own/ (FULL and THUMB) and assets/resp/ (480/960 px for phones). Originals, for the
   pipeline: docs/own-photos/. When the library is next rebuilt with these photos in it, delete this file and its
   <script> tags. Captions say only what the photo shows. */
(function () {
  'use strict';
  var L = window.SHIVAS_LIBRARY; if (!L || !L.assets || !L.items) return;
  var A = {
 "kettle-photo-own-12516efb50": {
  "type": "photo",
  "tag": "Photo",
  "alt": "Photo: Zinc kettle on its furnace base, with ceramic fibre insulation pinned along the lower edges",
  "config": "Zinc kettle on its furnace base, with ceramic fibre insulation pinned along the lower edges",
  "verified": true,
  "preview": "assets/own/kettle-photo-own-12516efb50_THUMB.webp",
  "preview_w": 720,
  "preview_h": 480,
  "thumb": "assets/own/kettle-photo-own-12516efb50_THUMB.webp",
  "thumb_w": 720,
  "thumb_h": 480,
  "full": "assets/own/kettle-photo-own-12516efb50_FULL.webp",
  "full_w": 1600,
  "full_h": 1200
 },
 "kettle-photo-own-5b5ef5e244": {
  "type": "photo",
  "tag": "Photo",
  "alt": "Photo: Zinc kettle in the shop: insulation pins welded on, ceramic fibre and a stainless steel cover sheet being fitted",
  "config": "Zinc kettle in the shop: insulation pins welded on, ceramic fibre and a stainless steel cover sheet being fitted",
  "verified": true,
  "preview": "assets/own/kettle-photo-own-5b5ef5e244_THUMB.webp",
  "preview_w": 720,
  "preview_h": 480,
  "thumb": "assets/own/kettle-photo-own-5b5ef5e244_THUMB.webp",
  "thumb_w": 720,
  "thumb_h": 480,
  "full": "assets/own/kettle-photo-own-5b5ef5e244_FULL.webp",
  "full_w": 1200,
  "full_h": 1600
 },
 "slm-photo-own-12cbae9704": {
  "type": "photo",
  "tag": "Photo",
  "alt": "Photo: Drawing block of a straight line machine, with the rotating die box beside it",
  "config": "Drawing block of a straight line machine, with the rotating die box beside it",
  "verified": true,
  "preview": "assets/own/slm-photo-own-12cbae9704_THUMB.webp",
  "preview_w": 720,
  "preview_h": 480,
  "thumb": "assets/own/slm-photo-own-12cbae9704_THUMB.webp",
  "thumb_w": 720,
  "thumb_h": 480,
  "full": "assets/own/slm-photo-own-12cbae9704_FULL.webp",
  "full_w": 1600,
  "full_h": 1200
 },
 "diebox-photo-own-a44362b187": {
  "type": "photo",
  "tag": "Photo",
  "alt": "Photo: Rotating die box with its geared motor under the white guard, drawing block behind",
  "config": "Rotating die box with its geared motor under the white guard, drawing block behind",
  "verified": true,
  "preview": "assets/own/diebox-photo-own-a44362b187_THUMB.webp",
  "preview_w": 720,
  "preview_h": 480,
  "thumb": "assets/own/diebox-photo-own-a44362b187_THUMB.webp",
  "thumb_w": 720,
  "thumb_h": 480,
  "full": "assets/own/diebox-photo-own-a44362b187_FULL.webp",
  "full_w": 1200,
  "full_h": 1600
 },
 "slm-photo-own-3849c2346c": {
  "type": "photo",
  "tag": "Photo",
  "alt": "Photo: Straight line machine: drawing block between two die boxes, with the wire guide roller",
  "config": "Straight line machine: drawing block between two die boxes, with the wire guide roller",
  "verified": true,
  "preview": "assets/own/slm-photo-own-3849c2346c_THUMB.webp",
  "preview_w": 720,
  "preview_h": 480,
  "thumb": "assets/own/slm-photo-own-3849c2346c_THUMB.webp",
  "thumb_w": 720,
  "thumb_h": 480,
  "full": "assets/own/slm-photo-own-3849c2346c_FULL.webp",
  "full_w": 1600,
  "full_h": 1200
 },
 "slm-photo-own-825e2992cd": {
  "type": "photo",
  "tag": "Photo",
  "alt": "Photo: Straight line wire drawing machine, new, hood raised, still in its protective film",
  "config": "Straight line wire drawing machine, new, hood raised, still in its protective film",
  "verified": true,
  "preview": "assets/own/slm-photo-own-825e2992cd_THUMB.webp",
  "preview_w": 720,
  "preview_h": 480,
  "thumb": "assets/own/slm-photo-own-825e2992cd_THUMB.webp",
  "thumb_w": 720,
  "thumb_h": 480,
  "full": "assets/own/slm-photo-own-825e2992cd_FULL.webp",
  "full_w": 1200,
  "full_h": 1600
 },
 "wire-photo-own-d727f92851": {
  "type": "photo",
  "tag": "Photo",
  "alt": "Photo: Rotating head with two roller straighteners, inside its guarded cabinet, in the SHIVAS shop",
  "config": "Rotating head with two roller straighteners, inside its guarded cabinet, in the SHIVAS shop",
  "verified": true,
  "preview": "assets/own/wire-photo-own-d727f92851_THUMB.webp",
  "preview_w": 720,
  "preview_h": 480,
  "thumb": "assets/own/wire-photo-own-d727f92851_THUMB.webp",
  "thumb_w": 720,
  "thumb_h": 480,
  "full": "assets/own/wire-photo-own-d727f92851_FULL.webp",
  "full_w": 1200,
  "full_h": 1600
 },
 "diebox-photo-own-be841dd299": {
  "type": "photo",
  "tag": "Photo",
  "alt": "Photo: Rotating die box: entry guide roller, die holder and the geared motor that turns the die",
  "config": "Rotating die box: entry guide roller, die holder and the geared motor that turns the die",
  "verified": true,
  "preview": "assets/own/diebox-photo-own-be841dd299_THUMB.webp",
  "preview_w": 720,
  "preview_h": 480,
  "thumb": "assets/own/diebox-photo-own-be841dd299_THUMB.webp",
  "thumb_w": 720,
  "thumb_h": 480,
  "full": "assets/own/diebox-photo-own-be841dd299_FULL.webp",
  "full_w": 1200,
  "full_h": 1600
 },
 "diebox-photo-own-62021afd68": {
  "type": "photo",
  "tag": "Photo",
  "alt": "Photo: Rotating die boxes along a straight line machine, each with its own geared motor",
  "config": "Rotating die boxes along a straight line machine, each with its own geared motor",
  "verified": true,
  "preview": "assets/own/diebox-photo-own-62021afd68_THUMB.webp",
  "preview_w": 720,
  "preview_h": 480,
  "thumb": "assets/own/diebox-photo-own-62021afd68_THUMB.webp",
  "thumb_w": 720,
  "thumb_h": 480,
  "full": "assets/own/diebox-photo-own-62021afd68_FULL.webp",
  "full_w": 1600,
  "full_h": 1200
 },
 "slm-photo-own-51015c0838": {
  "type": "photo",
  "tag": "Photo",
  "alt": "Photo: Straight line wire drawing machine, full length, with the hood raised",
  "config": "Straight line wire drawing machine, full length, with the hood raised",
  "verified": true,
  "preview": "assets/own/slm-photo-own-51015c0838_THUMB.webp",
  "preview_w": 720,
  "preview_h": 480,
  "thumb": "assets/own/slm-photo-own-51015c0838_THUMB.webp",
  "thumb_w": 720,
  "thumb_h": 480,
  "full": "assets/own/slm-photo-own-51015c0838_FULL.webp",
  "full_w": 1200,
  "full_h": 1600
 }
};
  var G = {
 "kettle": {
  "after": "kettle-photo-own-c4692d09b4",
  "add": [
   "kettle-photo-own-12516efb50",
   "kettle-photo-own-5b5ef5e244"
  ]
 },
 "slm": {
  "image": "slm-photo-own-51015c0838",
  "first": [
   "slm-photo-own-51015c0838",
   "slm-photo-own-825e2992cd",
   "slm-photo-own-3849c2346c",
   "slm-photo-own-12cbae9704"
  ]
 },
 "diebox": {
  "after": "diebox-photo-own-fa22d6fda9",
  "add": [
   "diebox-photo-own-be841dd299",
   "diebox-photo-own-a44362b187",
   "diebox-photo-own-62021afd68"
  ]
 }
};
  var k, i, it, g, n;
  for (k in A) L.assets[k] = A[k];
  for (k in G) {
    it = L.items[k]; g = G[k]; if (!it) continue;
    it.gallery = (it.gallery || []).filter(function (x) { return !A[x]; });
    if (g.first) it.gallery = g.first.concat(it.gallery);
    if (g.add) { i = it.gallery.indexOf(g.after); Array.prototype.splice.apply(it.gallery, [i < 0 ? 0 : i + 1, 0].concat(g.add)); }
    if (g.image) it.image = g.image;
    n = 0; it.gallery.forEach(function (x) { if (L.assets[x] && L.assets[x].type === 'photo') n++; }); it.photos = n;
  }
})();
