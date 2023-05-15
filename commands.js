import { error_embed, track_list, playerList } from './utils.js';
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
    let time = new Date().getTime()
    if (interaction.isAutocomplete()) {
        let focusedValue = interaction.options.getFocused(true)

        switch (focusedValue.name) {
            case "track":
                const tracks = track_list
                let f_tracks = tracks.filter(track => track.toLowerCase().startsWith(focusedValue.value.toLowerCase()))
                return await interaction.respond(
                    f_tracks.map(track => ({ name: track, value: track })).slice(0, 25),
                )

            case "player":
                const players = playerList
                let f_player = players.filter(player => player.toLowerCase().startsWith(focusedValue.value.toLowerCase()))
                return await interaction.respond(
                    f_player.map(player => ({ name: player, value: player })).slice(0, 25),
                )

            default:
                return
        }
    }

    if (!interaction.isChatInputCommand()) return;
    if (interaction.acknowledged) return;
    if (interaction.guildId == null && server_commands.some(s_cmd => interaction.commandName.includes(s_cmd))) return error_embed(interaction, "sorry, but this command can only be used in a server")

    let command_options = []

    for (let i = 0; i < interaction.options._hoistedOptions.length; i++) {
        command_options.push({ name: interaction.options._hoistedOptions[i].name, value: interaction.options._hoistedOptions[i].value.length > 1024 ? "Too many chars to display" : interaction.options._hoistedOptions[i].value })
    }

    let commandLogEmbed = new EmbedBuilder()
        .setAuthor({ name: interaction.user.username + '#' + interaction.user.discriminator, iconURL: interaction.user.avatarURL() })
        .setTitle('/' + interaction.commandName)
        .setTimestamp()
        .setFooter({ text: interaction.guild != undefined ? interaction.guild.name : "direct message", iconURL: interaction.guild != undefined ? interaction.guild.iconURL() : null })
        .addFields(command_options)

    let logs_message = client.channels.cache.get(`1065611483897147502`).send({ embeds: [commandLogEmbed] });

    switch (interaction.commandName) {
        case 'save_time':
            await commands.save_time(interaction);
            break;
        case 'delete_time':
            await commands.delete_time(interaction);
            break;
        case 'import_times':
            await commands.import_times(interaction);
            break;
        case 'display_time':
            await commands.display_time(interaction);
            break;
        case 'help':
            await commands.help(interaction);
            break;
        case 'register_user':
            await commands.register_user(interaction);
            break;
        case 'remove_user':
            await commands.remove_user(interaction);
            break;
        case 'team_stats':
            await commands.team_stats(interaction);
            break;
        case 'name_history':
            await commands.name_history(interaction);
            break;
        case 'lineup':
            await commands.lineup(interaction);
            break;
        case 'tracks':
            await commands.tracks(interaction);
            break;
        default:
            break;
    }
    commandLogEmbed.setColor(0xb4ffb1)
    commandLogEmbed.setTitle('/' + interaction.commandName + ' ``(' + ((new Date().getTime() - time)/ 1000)+ 's)``')
    logs_message = await Promise.resolve(logs_message)
    logs_message.edit({ embeds: [commandLogEmbed] })
}