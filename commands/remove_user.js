import { user_list, error_embed } from "../utils.js";

import { EmbedBuilder, } from "discord.js";

export const remove_user = async (interaction) => {
    try {
        if (user_list[interaction.guild.id] == undefined) {
            user_list[interaction.guild.id] = [];
        }
        var user_id = interaction.options.get("user").value.replace(/[^0-9]/g, '');
        if (!user_list[interaction.guild.id].includes(user_id)) {
            return error_embed(interaction, "sorry, but this user is invalid or not registered in this server");
        }
        user_list[interaction.guild.id].splice(user_list[interaction.guild.id].indexOf(user_id), 1);
        interaction.reply({
            embeds: [
                new EmbedBuilder()
                    .setTitle("User removed")
                    .setColor(0x47e0ff)
                    .setDescription(`${user_id} has been removed from this server`)
                    .setThumbnail(interaction.guild.iconURL()),
            ],
        })
    } catch (e) {
        throw e;
    }
}