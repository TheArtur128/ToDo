import { Dirty } from "../fp";

export const alertNotifications = {
    with(message: string): Dirty<typeof this> {
        alert(message);
        return this;
    }
}

export const consoleErrorLogs = {
    with(message: string): Dirty<typeof this> {
        console.error(message);
        return this;
    }
}
