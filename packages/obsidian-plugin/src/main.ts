import { Notice, Plugin } from "obsidian";

export default class FeishuObsidianLocalStatusPlugin extends Plugin {
  async onload() {
    this.addRibbonIcon("radio-tower", "Open local product status", () => {
      new Notice("Status panel will be added in the next step.");
    });
  }
}
