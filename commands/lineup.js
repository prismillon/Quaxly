import { TextInputBuilder, ModalBuilder, TextInputStyle, ActionRowBuilder, ButtonBuilder } from 'discord.js'
import { error_embed } from '../utils.js'

export const lineup = async (interaction) => {
    try {
        let player_id_list = interaction.options.get("players").value.split('<@').filter(e => e != '').map(e => e.replace(/[^0-9]/g, ''))
        player_id_list = [...new Set(player_id_list)]
        let players = player_id_list.map(e => `<@${e}>`).join(' - ')
        let host = interaction.options.get("host").value
        let tag = interaction.options.get("tag").value
        let time = interaction.options.get("time").value
        let ennemy_tag = interaction.options.get("ennemy_tag").value

        if (host.includes('-') && host.replaceAll(' ', '').length == 14) {
            let json = await (await fetch("https://www.mk8dx-lounge.com/api/player?fc=" + host + "&quaxly=true")).json()
            if (json.discordId != undefined) host = `${json.switchFc} (<@${json.discordId}>)`
        }
        else {
            let json = await (await fetch("https://www.mk8dx-lounge.com/api/player?discordid=" + host.replace(/[^0-9-]/g, '') + "&quaxly=true")).json()
            if (json.switchFc != undefined) host = `${json.switchFc} (<@${json.discordId}>)`
        }
        let embed = {
            title: `Clan war | ${tag} vs ${ennemy_tag}`,
            color: 16758711,
            fields: [
                {
                    name: "__Lineup__",
                    value: players
                },
                {
                    name: "__Open__",
                    value: '`' + time + '`',
                    inline: true
                },
                {
                    name: "__Host__",
                    value: host,
                    inline: true
                }
            ],
            thumbnail: {
                url: interaction.guild.iconURL()
            }
        }
        const buttonDefault = new ActionRowBuilder()
            .addComponents(
                new ButtonBuilder()
                    .setCustomId('edit_lineup')
                    .setLabel('Edit')
                    .setStyle('Secondary'),
                new ButtonBuilder()
                    .setCustomId('add_player')
                    .setLabel('Add player')
                    .setStyle('Secondary'),
                new ButtonBuilder()
                    .setCustomId('remove_player')
                    .setLabel('Remove player')
                    .setStyle('Secondary')
            )
        const buttonFull = new ActionRowBuilder()
            .addComponents(
                new ButtonBuilder()
                    .setCustomId('edit_lineup')
                    .setLabel('Edit')
                    .setStyle('Secondary'),
                new ButtonBuilder()
                    .setCustomId('add_player')
                    .setLabel('Add player')
                    .setStyle('Secondary')
                    .setDisabled(true),
                new ButtonBuilder()
                    .setCustomId('remove_player')
                    .setLabel('Remove player')
                    .setStyle('Secondary')
            )
        let button = embed.fields[0].value.split(' - ').length == 6 ? buttonFull : buttonDefault
        interaction.reply({ content: `lineup war ${time} vs ${ennemy_tag} ||${players}||`, embeds: [embed], components: [button] }).then(() => {
            interaction.editReply({ content: '', embeds: [embed], components: [button] })
        })
        const collector = interaction.channel.createMessageComponentCollector({
            filter: i => i.user.id === interaction.user.id,
            time: 28800000,
        })
        collector.on('end', async () => {
            try {
                await interaction.editReply({ content: '', embeds: [embed], components: [] })
            } catch (error) {
            }
            collector.stop();
        })
        collector.on('collect', async i => {
            if (i.customId === 'edit_lineup') {
                const modal_edit_lineup = new ModalBuilder()
                    .setCustomId('modal_edit_lineup')
                    .setTitle('You have 10 minute to edit')
                const input_host = new TextInputBuilder()
                    .setCustomId('input_host')
                    .setLabel('Host')
                    .setPlaceholder(`Input a discord id or a FC`)
                    .setMinLength(1)
                    .setMaxLength(30)
                    .setRequired(false)
                    .setStyle(TextInputStyle.Short);
                const input_time = new TextInputBuilder()
                    .setCustomId('input_time')
                    .setLabel('Time')
                    .setPlaceholder(`${time}`)
                    .setMinLength(1)
                    .setMaxLength(20)
                    .setRequired(false)
                    .setStyle(TextInputStyle.Short);
                const input_ennemy_tag = new TextInputBuilder()
                    .setCustomId('input_ennemy_tag')
                    .setLabel('Ennemy tag')
                    .setPlaceholder(`${ennemy_tag}`)
                    .setMinLength(1)
                    .setMaxLength(20)
                    .setRequired(false)
                    .setStyle(TextInputStyle.Short);
                const input_tag = new TextInputBuilder()
                    .setCustomId('input_tag')
                    .setLabel('Tag')
                    .setPlaceholder(`${tag}`)
                    .setMinLength(1)
                    .setMaxLength(20)
                    .setRequired(false)
                    .setStyle(TextInputStyle.Short);
                const first_row = new ActionRowBuilder()
                    .addComponents(input_time)
                const second_row = new ActionRowBuilder()
                    .addComponents(input_host)
                const third_row = new ActionRowBuilder()
                    .addComponents(input_ennemy_tag)
                const fourth_row = new ActionRowBuilder()
                    .addComponents(input_tag)
                modal_edit_lineup.addComponents(first_row, second_row, third_row, fourth_row)
                i.showModal(modal_edit_lineup)
                const filter = (interaction) => interaction.customId === 'modal_edit_lineup';
                i.awaitModalSubmit({ filter, time: 600000 }).then(async i => {
                    try {
                        i.fields.getTextInputValue('input_time') ? time = i.fields.getTextInputValue('input_time') : time = time
                        i.fields.getTextInputValue('input_host') ? host = i.fields.getTextInputValue('input_host') : host = host
                        i.fields.getTextInputValue('input_ennemy_tag') ? ennemy_tag = i.fields.getTextInputValue('input_ennemy_tag') : ennemy_tag = ennemy_tag
                        i.fields.getTextInputValue('input_tag') ? tag = i.fields.getTextInputValue('input_tag') : tag = tag
                        if (i.fields.getTextInputValue('input_host')) {
                            let json = await (await fetch("https://www.mk8dx-lounge.com/api/player?discordid=" + host + "&quaxly=true")).json()
                            if (json.switchFc != undefined) host = `${json.switchFc} (<@${json.discordId}>)`
                            else {
                                json = await (await fetch("https://www.mk8dx-lounge.com/api/player?fc=" + host + "&quaxly=true")).json()
                                if (json.discordId != undefined) host = `${json.switchFc} (<@${json.discordId}>)`
                            }
                        }
                        embed.fields[1].value = '`' + time + '`'
                        embed.fields[2].value = host
                        embed.title = `Clan war | ${tag} vs ${ennemy_tag}`
                        await i.update({ embeds: [embed] })
                    } catch (error) {
                    }
                })
            }
            if (i.customId === 'add_player') {
                const modal_add_player = new ModalBuilder()
                    .setCustomId('modal_add_player')
                    .setTitle('add player')
                const input_player = new TextInputBuilder()
                    .setCustomId('input_player')
                    .setLabel('Player')
                    .setPlaceholder('player id')
                    .setMinLength(1)
                    .setMaxLength(30)
                    .setRequired(true)
                    .setStyle(TextInputStyle.Short);
                const first_row = new ActionRowBuilder()
                    .addComponents(input_player)
                modal_add_player.addComponents(first_row)
                i.showModal(modal_add_player)
                const filter = (interaction) => interaction.customId === 'modal_add_player';
                i.awaitModalSubmit({ filter, time: 60000 }).then(async i => {
                    try {
                        await i.guild.members.fetch(i.fields.getTextInputValue('input_player')).then(async () => {
                            if (!players.includes('<@' + i.fields.getTextInputValue('input_player') + '>')) {
                                players = players + ' - <@' + i.fields.getTextInputValue('input_player') + '>'
                                embed.fields[0].value = players
                                button = embed.fields[0].value.split(' - ').length == 6 ? buttonFull : buttonDefault
                                await i.update({ embeds: [embed], components: [button] })
                            } else {
                                await error_embed(i, `<@${i.fields.getTextInputValue('input_player')}> is already in the lineup`)
                            }
                        }).catch(async () => {
                            await error_embed(i, 'Player not found in this server, double check the id')
                        })
                    } catch (error) {
                    }
                })
            }
            if (i.customId === 'remove_player') {
                const modal_remove_player = new ModalBuilder()
                    .setCustomId('modal_remove_player')
                    .setTitle('remove player')
                const input_player = new TextInputBuilder()
                    .setCustomId('input_player')
                    .setLabel('Player')
                    .setPlaceholder('player id')
                    .setMinLength(1)
                    .setMaxLength(30)
                    .setRequired(true)
                    .setStyle(TextInputStyle.Short);
                const first_row = new ActionRowBuilder()
                    .addComponents(input_player)
                modal_remove_player.addComponents(first_row)
                i.showModal(modal_remove_player)
                const filter = (interaction) => interaction.customId === 'modal_remove_player';
                i.awaitModalSubmit({ filter, time: 60000 }).then(async i => {
                    try {
                        if (players.includes('<@' + i.fields.getTextInputValue('input_player') + '>')) {
                            players = players.replace(' - <@' + i.fields.getTextInputValue('input_player') + '>', '')
                            players = players.replace('<@' + i.fields.getTextInputValue('input_player') + '> - ', '')
                            players = players.replace('<@' + i.fields.getTextInputValue('input_player') + '>', '')
                            embed.fields[0].value = players
                            button = embed.fields[0].value.split(' - ').length == 6 ? buttonFull : buttonDefault
                            await i.update({ embeds: [embed], components: [button] })
                        } else {
                            await error_embed(i, 'Player is not in the lineup, double check the id')
                        }
                    } catch (error) {
                    }
                })
            }
        })
    } catch (e) {
        throw e;
    }
}