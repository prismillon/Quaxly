import { error_embed } from './utils.js';
import { client } from './Quaxly.js';
import { delete_time } from './commands/delete_time.js';
import { display_time } from './commands/display_time.js';
import { help } from './commands/help.js';
import { import_times } from './commands/import_times.js';
import { register_user } from './commands/register_user.js';
import { remove_user } from './commands/remove_user.js';
import { save_time } from './commands/save_time.js';
import { team_stats } from './commands/team_stats.js';
import { name_history } from './commands/name_history.js';
import { lineup } from './commands/lineup.js';
import { tracks } from './commands/tracks.js';
import { EmbedBuilder } from '@discordjs/builders';

const commands = { save_time, delete_time, import_times, display_time, help, register_user, remove_user, team_stats, name_history, lineup, tracks }

const server_commands = ['time', 'user', 'lineup', 'tracks']

export const CommandHandler = async (interaction) => {
    if (!interaction.isChatInputCommand()) return;
    if (interaction.acknowledged) return;
    if (interaction.guildId == null && server_commands.some(s_cmd => interaction.commandName.includes(s_cmd))) return error_embed(interaction, "sorry, but this bot can only be used in a server")

    let command_options = []

    for (let i = 0; i < interaction.options._hoistedOptions.length; i++) {
        command_options.push({ name: interaction.options._hoistedOptions[i].name, value: interaction.options._hoistedOptions[i].value.length > 1024 ? "Too many chars to display" : interaction.options._hoistedOptions[i].value })
    }

    const commandLogEmbed = new EmbedBuilder()
        .setAuthor({ name: interaction.user.username + '#' + interaction.user.discriminator, iconURL: interaction.user.avatarURL() })
        .setTitle('/' + interaction.commandName)
        .setTimestamp()
        .setFooter({ text: interaction.user.id })
        .addFields(command_options)

    client.channels.cache.get(`1065611483897147502`).send({ embeds: [commandLogEmbed] });

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
        case 'team_stats':
            commands.team_stats(interaction);
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