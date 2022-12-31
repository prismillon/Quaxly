import { track_list } from "../utils.js";

import { EmbedBuilder, } from "discord.js";

export const help = async (interaction) => {
    try {
        let new_tracks = track_list.slice(-8);
        let new_tracks_string = "";
        for (let i = 0; i < new_tracks.length; i++) {
            new_tracks_string += `\`${new_tracks[i]}\` `;
        }
        interaction.reply({
            embeds: [
                new EmbedBuilder()
                    .setTitle("Help menu")
                    .setColor(0x47e0ff)
                    .setThumbnail("https://archives.bulbagarden.net/media/upload/4/49/Quaxly.png")
                    .setFooter({ text: "Made by pierre#1111, feel free to contact me if you have any questions" })
                    .addFields({
                        name: "/ping",
                        value: "Returns the bot's latency",

                    },
                        {
                            name: "/save_time",
                            value: "Saves your time in the chosen category",
                        },
                        {
                            name: "/delete_time",
                            value: "Deletes times based on the parameters you provide",
                        },
                        {
                            name: "/import_times",
                            value: "Import times from Cadoizzob#8500's bot, copy paste the text from the bot in the list field",
                        },
                        {
                            name: "/display_time",
                            value: "Displays your times based on the parameters you provide",
                        },
                        {
                            name: "/register_user",
                            value: "Register the user selected in the server",
                        },
                        {
                            name: "/remove_user",
                            value: "Remove the user selected from the server",
                        },
                        {
                            name: "Last 8 dlc tracks names in order:",
                            value: new_tracks_string,
                        }
                    )
            ],
        })
    } catch (e) {
        throw e;
    }
}