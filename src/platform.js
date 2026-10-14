/* Platform layer: gives the games the small "claude.use('db'|'user')" API they were written against,
   backed by Firebase (Firestore for data, Auth for identity). Games and shell never talk to Firebase directly.
   If window.claude already exists (the test harness provides a mock) this file does nothing. */
/* Games run in iframes, so the objects they write were created in another JavaScript realm. Firestore rejects such
   objects ("custom Object"), so every write is copied into this page's realm first. Also: update() on a missing
   doc creates it (the games rely on that). */
window.TGPatchFirestore = function (fb) {
  var clone = function (v) { return v === undefined ? v : JSON.parse(JSON.stringify(v)); };
  var DR = fb.firestore.DocumentReference.prototype, CR = fb.firestore.CollectionReference.prototype;
  var set = DR.set, upd = DR.update, add = CR.add;
  DR.set = function (d, o) { return o === undefined ? set.call(this, clone(d)) : set.call(this, clone(d), o); };
  CR.add = function (d) { return add.call(this, clone(d)); };
  DR.update = function () {
    var self = this, args = Array.prototype.slice.call(arguments);
    if (args.length === 1) args[0] = clone(args[0]);
    return upd.apply(this, args).catch(function (e) {
      if (e && e.code === "not-found" && args.length === 1) return set.call(self, args[0], { merge: true });
      throw e;
    });
  };
};

(function () {
  if (window.claude) return;
  var cfg = window.TG_FIREBASE || {};
  var BASE = "https://www.gstatic.com/firebasejs/10.12.2/";
  var ready = null, A = null;

  function load(src) {
    return new Promise(function (res, rej) {
      var s = document.createElement("script");
      s.src = src; s.onload = res; s.onerror = function () { rej(new Error("Could not load " + src)); };
      document.head.appendChild(s);
    });
  }
  function boot() {
    if (ready) return ready;
    ready = (async function () {
      if (!cfg.apiKey || /YOUR_/.test(cfg.apiKey)) throw new Error("Firebase is not configured: edit src/firebase-config.js");
      await load(BASE + "firebase-app-compat.js");
      await load(BASE + "firebase-auth-compat.js");
      await load(BASE + "firebase-firestore-compat.js");
      firebase.initializeApp(cfg);
      var auth = firebase.auth(), fs = firebase.firestore();
      fs.settings({ ignoreUndefinedProperties: true });
      window.TGPatchFirestore(firebase);
      var u = await new Promise(function (r) { var off = auth.onAuthStateChanged(function (x) { off(); r(x); }); });
      if (!u) await auth.signInAnonymously();
      A = { auth: auth, fs: fs };
      return A;
    })();
    ready.catch(function (e) { console.error(e); });
    return ready;
  }

  window.claude = {
    use: async function (name) {
      try {
        var a = await boot();
        if (name === "db") return a.fs;
        if (name === "user") {
          return {
            id: async function () { return a.auth.currentUser.uid; },
            me: async function () { return { id: a.auth.currentUser.uid }; },
            isOwner: function () { return false; }, canEdit: function () { return true; },
            can: function () { return true; }, profiles: async function () { return {}; }
          };
        }
      } catch (e) { console.error(e); }
      return null;
    }
  };

  /* ---- accounts: guest by default; upgrade keeps the same id, so games carry over ---- */
  var DOMAIN = "@players.invalid";
  function cleanName(n) {
    n = String(n || "").trim().toLowerCase();
    if (!/^[a-z0-9._-]{3,30}$/.test(n)) throw new Error("Username: 3–30 letters, numbers, dot, dash or underscore.");
    return n;
  }
  function msg(e) {
    var c = e && e.code || "";
    if (c === "auth/email-already-in-use" || c === "auth/credential-already-in-use") return "That username is taken.";
    if (c === "auth/weak-password") return "Password must be at least 6 characters.";
    if (c === "auth/invalid-credential" || c === "auth/wrong-password" || c === "auth/user-not-found" || c === "auth/invalid-login-credentials") return "Wrong username or password.";
    if (c === "auth/popup-closed-by-user" || c === "auth/cancelled-popup-request") return "";
    if (c === "auth/operation-not-allowed") return "That sign-in method is not enabled in Firebase yet.";
    return (e && e.message) || "Something went wrong.";
  }
  window.TGAuth = {
    ready: boot,
    info: function () {
      var u = A && A.auth.currentUser; if (!u) return null;
      var n = u.displayName || (u.email && u.email.indexOf(DOMAIN) > 0 ? u.email.split("@")[0] : u.email) || "";
      return { uid: u.uid, guest: u.isAnonymous, name: n };
    },
    google: async function () {
      var a = await boot(), p = new firebase.auth.GoogleAuthProvider(), u = a.auth.currentUser;
      try {
        if (u && u.isAnonymous) await u.linkWithPopup(p); else await a.auth.signInWithPopup(p);
      } catch (e) {
        if (e && e.code === "auth/credential-already-in-use" && e.credential) await a.auth.signInWithCredential(e.credential);
        else throw new Error(msg(e));
      }
    },
    signUp: async function (name, pw) {
      var a = await boot(), n = cleanName(name), u = a.auth.currentUser;
      try {
        if (u && u.isAnonymous) { await u.linkWithCredential(firebase.auth.EmailAuthProvider.credential(n + DOMAIN, pw)); u = a.auth.currentUser; }
        else u = (await a.auth.createUserWithEmailAndPassword(n + DOMAIN, pw)).user;
        await u.updateProfile({ displayName: n });
      } catch (e) { throw new Error(msg(e)); }
    },
    signIn: async function (name, pw) {
      var a = await boot();
      try { await a.auth.signInWithEmailAndPassword(cleanName(name) + DOMAIN, pw); } catch (e) { throw new Error(msg(e)); }
    },
    signOut: async function () { var a = await boot(); await a.auth.signOut(); }
  };
})();
