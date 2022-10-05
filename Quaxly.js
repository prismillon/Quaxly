const { Client, GatewayIntentBits, REST, Routes } = require('discord.js');
const client = new Client({ intents: [GatewayIntentBits.Guilds] });
const token = require('./config.json');
const { readFileSync } = require('fs');

client.on('ready', () => {
  console.log(`Logged in as ${client.user.tag}!`);
});

const track_list = readFileSync("./tracklist.txt", 'utf-8').split(/\r?\n/);

client.on('interactionCreate', async interaction => {
  if (!interaction.isChatInputCommand()) return;

  if (interaction.commandName === 'ping') {
    await interaction.reply({content: 'Pong! took ' + client.ws.ping + ' ms', ephemeral: true});
  }
  if (interaction.commandName === 'select') {
    await interaction.reply({content: `selected ${interaction.options.get('colors').value} and ${interaction.options.get('numbers').value}`, ephemeral: true});
  }
  if (interaction.commandName === 'save_time') {
    const speed = interaction.options.get('speed').value;
    track = interaction.options.get('track').value;
    for (let i = 0; i < track_list.length; i++) {
        if (track_list[i].toLowerCase() == track.toLowerCase()) {
            track = track_list[i];
            break;
        }
        if (i == track_list.length - 1) {
            await interaction.reply({content: `Track not found`, ephemeral: true});
            return;
        }
    }
    const time = interaction.options.get('time').value;
    const reg = new RegExp('^[0-9]:[0-9]{2}\\.[0-9]{3}$');
    if (!reg.test(time)) {
        await interaction.reply({content: `Invalid time format (\`${time}\`), please use this format -> \`1:23.456\``, ephemeral: true});
        return;
    }
    shroom = 'NI';
    if (interaction.options.get('shroom').value == 1) {
        shroom = 'Shroom';
    }
    await interaction.reply({content: `Saved **${time}** on \`${track}\` in ${speed}cc (${shroom}) !`});
  }
});

client.login(token.Quaxly);