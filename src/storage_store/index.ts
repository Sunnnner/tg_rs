import { Store } from "@thenbe/tauri-plugin-store-api";
import { configDir } from '@tauri-apps/api/path';

const appConfigDirPath = await configDir();

const store = new Store(appConfigDirPath+"config.json");

export default store;
