// notificationmanager.js
class notificationManager {
  constructor(options) {
    this.container = options.container || $("body");
    this.message = options.message || "";
    this.position = options.position || "topleft";
    this.type = options.type || "info";
    this.timeout = options.timeout || 3000;
  }

  show() {
    const notification = $('<div class="notification"></div>')
      .addClass(this.position)
      .addClass(this.type)
      .text(this.message);

    this.container.append(notification);

    setTimeout(() => {
      notification.fadeOut("slow", () => {
        notification.remove();
      });
    }, this.timeout);
  }
}
