import { TextInputBuilder, ModalBuilder, TextInputStyle, ActionRowBuilder, ButtonBuilder, InteractionCollector } from 'discord.js'
import { error_embed } from '../utils.js'

export const lineup = async (interaction) => {
    try {
        let uuid = '' + Date.now()
        let player_id_list = interaction.options.get("players").value.split('<@').filter(e => e != '').map(e => e.replace(/[^0-9]/g, ''))
        player_id_list = [...new Set(player_id_list)]
        let player_objects_list = Array.from((await interaction.guild.members.fetch()).filter(i => player_id_list.includes(i.user.id)), ([key, value]) => value).sort((a, b) => {
            if (a.user.username.toLowerCase() > b.user.username.toLowerCase()) return 1
            if (a.user.username.toLowerCase() < b.user.username.toLowerCase()) return -1
            return 0
        })
        let players = player_objects_list.map(e => `<@${e.user.id}>`).join(' - ')
        let host = interaction.options.get("host").value
        let tag = interaction.options.get("tag").value
        let time = interaction.options.get("time").value
        let ennemy_tag = interaction.options.get("ennemy_tag").value
        let json
        if (host.includes('-') && host.replaceAll(' ', '').length == 14) {
            try {
                json = await (await fetch("https://www.mk8dx-lounge.com/api/player?fc=" + host + "&quaxly=true")).json()
                if (json.discordId != undefined) host = `${json.switchFc} (<@${json.discordId}>)`
            } catch (error) {
            }
        }
        else {
            try {
                json = await (await fetch("https://www.mk8dx-lounge.com/api/player?discordid=" + host.replace(/[^0-9-]/g, '') + "&quaxly=true")).json()
                if (json.switchFc != undefined) host = `${json.switchFc} (<@${json.discordId}>)`
            }
            catch (error) {
            }
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
                    .setCustomId('button_edit' + uuid)
                    .setLabel('Edit')
                    .setStyle('Secondary'),
                new ButtonBuilder()
                    .setCustomId('button_add' + uuid)
                    .setLabel('Add player')
                    .setStyle('Secondary'),
                new ButtonBuilder()
                    .setCustomId('button_del' + uuid)
                    .setLabel('Remove player')
                    .setStyle('Secondary')
            )
        const buttonFull = new ActionRowBuilder()
            .addComponents(
                new ButtonBuilder()
                    .setCustomId('button_edit' + uuid)
                    .setLabel('Edit')
                    .setStyle('Secondary'),
                new ButtonBuilder()
                    .setCustomId('button_add' + uuid)
                    .setLabel('Add player')
                    .setStyle('Secondary')
                    .setDisabled(true),
                new ButtonBuilder()
                    .setCustomId('button_del' + uuid)
                    .setLabel('Remove player')
                    .setStyle('Secondary')
            )
        let button = embed.fields[0].value.split(' - ').length == 6 ? buttonFull : buttonDefault
        interaction.reply({ content: `lineup war ${time} vs ${ennemy_tag} ||${players}||`, embeds: [embed], components: [button] }).then(() => {
            interaction.editReply({ content: '', embeds: [embed], components: [button] })
        })
        const collector = new InteractionCollector(interaction.client, {
            filter: i => {
                if (i.customId !== undefined && i.customId.replace(/[^0-9]/gm, '') == uuid) {
                    if (i.user.id != interaction.user.id) i.reply({ content: `You can\'t use this button`, ephemeral: true })
                    return i.user.id === interaction.user.id
                }
                return false
            },
            time: 10800000,
        })
        collector.on('end', async () => {
            try {
                await interaction.editReply({ content: '', embeds: [embed], components: [] })
            } catch (error) {
                console.log(error);
            }
            collector.stop();
        })
        collector.on('collect', async i => {
            i.customId = i.customId.replace(/[0-9]/gm, '')
            if (i.customId === 'modal_edit_lineup') {
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
                }
                catch (error) {
                }
            }
            if (i.customId === 'modal_remove_player') {
                try {
                    await i.guild.members.fetch(i.fields.getTextInputValue('input_player')).then(async () => {
                        if (player_objects_list.some(obj => obj.user.id == i.fields.getTextInputValue('input_player'))) {
                            player_objects_list = player_objects_list.filter(obj => obj.user.id !== i.fields.getTextInputValue('input_player'))
                            embed.fields[0].value = player_objects_list.map(e => `<@${e.user.id}>`).join(' - ')
                            button = player_objects_list.length > 5 ? buttonFull : buttonDefault
                            await i.update({ embeds: [embed], components: [button] })
                        } else {
                            await error_embed(i, `<@${i.fields.getTextInputValue('input_player')}> is not in the lineup`)
                        }
                    })
                }
                catch (error) {
                    await error_embed(i, `<@${i.fields.getTextInputValue('input_player')}> is not a valid player`)
                }
            }
            if (i.customId === 'modal_add_player') {
                try {
                    await i.guild.members.fetch(i.fields.getTextInputValue('input_player')).then(async () => {
                        if (!player_objects_list.some(obj => obj.user.id == i.fields.getTextInputValue('input_player'))) {
                            let user = await interaction.guild.members.fetch(i.fields.getTextInputValue('input_player'))
                            player_objects_list.push(user)
                            player_objects_list = player_objects_list.sort((a, b) => {
                                if (a.user.username.toLowerCase() > b.user.username.toLowerCase()) return 1
                                if (a.user.username.toLowerCase() < b.user.username.toLowerCase()) return -1
                                return 0
                            })
                            embed.fields[0].value = player_objects_list.map(e => `<@${e.user.id}>`).join(' - ')
                            button = player_objects_list.length > 5 ? buttonFull : buttonDefault
                            await i.update({ embeds: [embed], components: [button] })
                        } else {
                            await error_embed(i, `<@${i.fields.getTextInputValue('input_player')}> is already in the lineup`)
                        }
                    })
                }
                catch (error) {
                    await error_embed(i, `<@${i.fields.getTextInputValue('input_player')}> is not a valid player`)
                }
            }
            if (i.customId === 'button_edit') {
                const modal_edit_lineup = new ModalBuilder()
                    .setCustomId('modal_edit_lineup' + uuid)
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
            }
            if (i.customId === 'button_add') {
                const modal_add_player = new ModalBuilder()
                    .setCustomId('modal_add_player' + uuid)
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
            }
            if (i.customId === 'button_del') {
                const modal_remove_player = new ModalBuilder()
                    .setCustomId('modal_remove_player' + uuid)
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
            }
        })
    } catch (e) {
        console.log(e);
        throw e;
    }
}