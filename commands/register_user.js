import { bdd, user_list, error_embed } from "../utils.js";

import { EmbedBuilder, } from "discord.js";

export const register_user = async (interaction) => {

    if (user_list[interaction.guild.id] == undefined) {
        user_list[interaction.guild.id] = [];
    }
    var user_id = interaction.options.get("user").value.replace(/[^0-9]/g, '');
    if (bdd[user_id] == undefined) {
        return error_embed(interaction, "sorry, but the user you provided is invalid or not registered in the database");
    }
    let user
    try {
        user = await interaction.guild.members.fetch(user_id)
    } catch (error) {
        return error_embed(interaction, "sorry, but the user you provided is not valid or not in this server");
    }
    if (user_list[interaction.guild.id].includes(user_id)) {
        return error_embed(interaction, "sorry, but this user is already registered in this server");
    }
    user_list[interaction.guild.id].push(user_id);
    interaction.reply({
        embeds: [
            new EmbedBuilder()
                .setTitle("User registered")
                .setColor(0x47e0ff)
                .setDescription(`${user.displayName} has been registered in this server`)
                .setThumbnail(user.displayAvatarURL()),
        ],
    })
}