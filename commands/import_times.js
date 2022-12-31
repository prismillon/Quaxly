import { bdd, user_and_server_id_check, player_update, get_track_formated, save_bdd, error_embed } from "../utils.js";

import { EmbedBuilder, } from "discord.js";

export const import_times = async (interaction) => {
    try {
        user_and_server_id_check(interaction.user.id, interaction.guild.id)
        player_update(interaction.user.id)
        const speed = interaction.options.get("speed").value;
        let item = "NI";
        if (interaction.options.get("item").value == 1) {
            item = "Shroom";
        }
        const list = interaction.options.get("list").value;
        const list_array = list.match(/[a-z,A-Z,0-9]+ : [0-9]+\/[0-9]+ -> [0-9]:[0-5][0-9]\.[0-9]{3}/g);
        if (list_array == null) {
            return error_embed(interaction, "could not find any time in the list you provided");
        }
        for (let i = 0; i < list_array.length; i++) {
            let track = get_track_formated(list_array[i].split(" : ")[0]);
            if (track == 0) continue;
            let time = list_array[i].split(" -> ")[1];
            bdd[interaction.user.id][speed][item][track] = time;
        }
        if (save_bdd() == 0) {
            return error_embed(interaction, `could not save the file as expected`);
        }
        const embed = new EmbedBuilder()
            .setTitle(`Times imported`)
            .setColor(0x47e0ff)
            .setDescription(`imported all your times from the list`);
        await interaction.reply({ embeds: [embed] });
    } catch (e) {
        throw e;
    }
}