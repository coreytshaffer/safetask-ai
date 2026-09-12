/* Standalone: must load even when legacy app.js fails to parse. */
(() => {
  const PAGE_VERSION = 2;
  const banner = document.getElementById("provenance-migration");
  const status = document.getElementById("provenance-migration-status");
  const reload = document.getElementById("provenance-reload");
  const incomplete = message => {
    banner.dataset.complete = "false";
    status.textContent = message;
    reload.hidden = false;
  };
  // Explicit user action only. No automatic navigation, including controllerchange.
  reload.addEventListener("click", () => window.location.reload());
  if (!("serviceWorker" in navigator)) {
    incomplete("Offline policy migration unavailable in this browser. No reviewed policy sources are supplied.");
    return;
  }
  async function checkController() {
    const controller = navigator.serviceWorker.controller;
    if (!controller) {
      incomplete("Policy cache migration pending. Save your work before reloading.");
      return;
    }
    if (controller.state !== "activated") {
      incomplete("Policy cache migration is activating. Keep your work open.");
      controller.addEventListener("statechange", checkController, {once: true});
      return;
    }
    const channel = new MessageChannel();
    const timeout = setTimeout(() => {
      channel.port1.close();
      incomplete("An older worker may still be active. Save your work, reconnect, then reload.");
    }, 2000);
    channel.port1.onmessage = event => {
      clearTimeout(timeout);
      channel.port1.close();
      const current = event.data?.workerVersion === PAGE_VERSION &&
        document.body.dataset.provenanceVersion === String(PAGE_VERSION) &&
        navigator.serviceWorker.controller === controller && !event.data.reloadRequired;
      if (current) {
        banner.dataset.complete = "true";
        status.textContent = "Policy cache migration complete. No reviewed policy sources are supplied.";
        reload.hidden = true;
      } else {
        incomplete("Policy cache migration requires a reload. Save your work first.");
      }
    };
    controller.postMessage({type: "SAFETASK_PROVENANCE_STATE_REQUEST", pageVersion: PAGE_VERSION}, [channel.port2]);
  }
  navigator.serviceWorker.addEventListener("controllerchange", checkController);
  navigator.serviceWorker.addEventListener("message", event => {
    if (event.data?.type === "SAFETASK_PROVENANCE_STATE") checkController();
  });
  navigator.serviceWorker.register("./sw.js", {updateViaCache: "none"})
    .then(async registration => { await registration.update(); checkController(); })
    .catch(() => {
      incomplete("Policy cache migration could not be verified. Reconnect, save your work, then reload.");
      checkController(); // A previously migrated page/worker can be verified while offline.
    });
})();
