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

    switch (interaction.commandName) {
        case 'save_time':
            commands.save_time(interaction);
            break;
        case 'delete_time':
            commands.delete_time(interaction);
            break;
        case 'import_times':
            commands.import_times(interaction);
            break;
        case 'display_time':
            commands.display_time(interaction);
            break;
        case 'help':
            commands.help(interaction);
            break;
        case 'register_user':
            commands.register_user(interaction);
            break;
        case 'remove_user':
            commands.remove_user(interaction);
            break;
        case 'team_mmr':
            commands.team_mmr(interaction);
            break;
        case 'name_history':
            commands.name_history(interaction);
            break;
        case 'lineup':
            commands.lineup(interaction);
            break;
        case 'tracks':
            commands.tracks(interaction);
            break;
        default:
            break;
    }
}