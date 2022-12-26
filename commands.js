import { error_embed } from './utils.js';

import { delete_time } from './commands/delete_time.js';
import { display_time } from './commands/display_time.js';
import { help } from './commands/help.js';
import { import_times } from './commands/import_times.js';
import { register_user } from './commands/register_user.js';
import { remove_user } from './commands/remove_user.js';
import { save_time } from './commands/save_time.js';
import { team_mmr } from './commands/team_mmr.js';
import { name_history } from './commands/name_history.js';
import { lineup } from './commands/lineup.js';
import { tracks } from './commands/tracks.js';

const commands = { save_time, delete_time, import_times, display_time, help, register_user, remove_user, team_mmr, name_history, lineup, tracks }

export const CommandHandler = async (interaction) => {
    if (!interaction.isChatInputCommand()) return;
    if (interaction.guildId == null) return error_embed(interaction, "sorry, but this bot can only be used in a server")

    if (interaction.commandName === "save_time") {
        commands.save_time(interaction)
    }
    if (interaction.commandName === "delete_time") {
        commands.delete_time(interaction)
    }
    if (interaction.commandName === "import_times") {
        commands.import_times(interaction)
    }
    if (interaction.commandName === "display_time") {
        commands.display_time(interaction)
    }
    if (interaction.commandName == "help") {
        commands.help(interaction)
    }
    if (interaction.commandName == "register_user") {
        commands.register_user(interaction)
    }
    if (interaction.commandName == "remove_user") {
        commands.remove_user(interaction)
    }
    if (interaction.commandName === "team_mmr") {
        commands.team_mmr(interaction)
    }
    if (interaction.commandName === "name_history") {
        commands.name_history(interaction)
    }
    if (interaction.commandName === "lineup") {
        commands.lineup(interaction)
    }
    if (interaction.commandName === "tracks") {
        commands.tracks(interaction)
    }
}