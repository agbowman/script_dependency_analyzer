import networkx as nx
from pyvis.network import Network
import json
from script_data import get_scripts

scripts = get_scripts()
# Step 2: Preprocess Scripts into a Dictionary
scripts_dict = {}
for script in scripts:
    scripts_dict[script["name"]] = {
        "da2_jobs": script.get("da2_jobs") or [],
        "ops_jobs": script.get("ops_jobs") or [],
        "calls": script.get("calls", [])
    }

# Convert the scripts dictionary to JSON for JavaScript consumption
scripts_json = json.dumps(scripts_dict)

# Step 3: Initialize an Empty Network with PyVis
net = Network(height="750px", width="100%", directed=True, notebook=False)
#
# Update network options to enhance visualization
net.set_options("""
{
    "nodes": {
        "shape": "dot",
        "size": 20,
        "font": {
            "multi": "html"
        },
        "fixed": {
            "x": false,
            "y": false
        }
    },
    "edges": {
        "color": {
            "color": "#848484",
            "highlight": "#FF0000"
        },
        "width": 1,
        "arrows": {
            "to": { "enabled": true, "scaleFactor": 1 }
        },
        "smooth": {
            "enabled": true,
            "type": "curvedCW",
            "roundness": 0.2
        }
    },
    "physics": {
        "enabled": true,
        "barnesHut": {
            "gravitationalConstant": -1000,
            "centralGravity": 0.05,
            "springLength": 200,
            "springConstant": 0.02,
            "damping": 0.3,
            "avoidOverlap": 0.5
        },
        "minVelocity": 0.1,
        "maxVelocity": 5,
        "solver": "barnesHut",
        "stabilization": {
            "enabled": true,
            "iterations": 1000,
            "updateInterval": 100,
            "onlyDynamicEdges": false,
            "fit": true
        }
    },
    "interaction": {
        "dragNodes": true,
        "dragView": true,
        "zoomView": true
    }
}
""")

# Step 4: Save and Read the Initial Empty Network
net.save_graph("script_dependency_graph.html")

with open("script_dependency_graph.html", "r", encoding="utf-8") as file:
    html_content = file.read()

# Step 5: Define Custom HTML and JavaScript for Dynamic Loading
custom_html = """
<!-- Search Box -->
<div id="searchBox" style="position: fixed; top: 10px; left: 10px; width: 350px; background: white; 
    padding: 10px; border: 1px solid black; border-radius: 5px; font-family: Arial; z-index: 1000;">
    <h3 style="margin-top: 0;">Search Scripts</h3>
    <label for="searchType">Search by:</label>
    <select id="searchType" style="width: 100%; padding: 5px; margin-bottom: 10px;">
        <option value="name">Name</option>
        <option value="da2">DA2 Job</option>
        <option value="ops">OPS Job</option>
    </select>
    <input list="scriptList" id="scriptSearchInput" name="scriptSearchInput" placeholder="Type to search..." style="width: 100%; padding: 5px; box-sizing: border-box;">
    <datalist id="scriptList">
        {options}
    </datalist>
    <button id="addScriptBtn" style="margin-top: 10px; padding: 5px 10px;">Add Script</button>
</div>

<!-- Selected Nodes List -->
<div id="selectedNodesContainer" style="position: fixed; top: 200px; left: 10px; width: 350px; background: white; 
    padding: 10px; border: 1px solid black; border-radius: 5px; font-family: Arial; z-index: 1000;">
    <h3 style="margin-top: 0;">Selected Scripts</h3>
    <ul id="selectedNodesList" style="list-style-type: none; padding-left: 0;">
        <!-- Selected scripts will appear here -->
    </ul>
</div>

<!-- Information Box -->
<div id="infoBox" style="position: fixed; top: 10px; right: 10px; width: 400px; background: white; 
    padding: 10px; border: 1px solid black; border-radius: 5px; font-family: Arial; max-height: 80vh; overflow-y: auto; z-index: 1000;">
    <h3 style="margin-top: 0;">Selected Nodes Info</h3>
    <div id="selectedNodesInfo"></div>
</div>
"""

# Generate datalist options based on script names only
script_options = "\n".join([f'<option value="{script["name"]}">' for script in scripts])
custom_html = custom_html.format(options=script_options)

# Correctly escaped custom_js with doubled curly braces and proper scriptId handling
custom_js = f"""
<script type="text/javascript">
    // Pre-computed scripts data
    const scriptsData = {scripts_json};

    // Keep track of selected nodes and their dependencies
    let selectedNodes = new Set();
    let addedNodes = new Set();
    let addedEdges = new Set();

    // Function to create node info HTML
    function createNodeInfoHTML(nodeId, directCalls, calledBy, indirectCalls, indirectCalledBy) {{
        // Helper function to get node attributes
        function getNodeJobs(nodeId) {{
            const script = scriptsData[nodeId];
            return {{
                da2_jobs: script.da2_jobs || [],
                ops_jobs: script.ops_jobs || []
            }};
        }}

        // Helper function to create jobs HTML
        function createJobsHTML(jobs) {{
            let da2_jobs = jobs.da2_jobs || [];
            let ops_jobs = jobs.ops_jobs || [];
            
            if (da2_jobs.length === 0 && ops_jobs.length === 0) return '';
            return `
                <div style="margin-left: 20px; font-size: 0.9em; color: #666;">
                    ${{jobs.da2_jobs.length > 0 ? `
                        <div>DA2 Jobs:</div>
                        <ul style="margin: 2px 0 5px 20px; padding: 0;">
                            ${{jobs.da2_jobs.map(job => `<li>${{job}}</li>`).join('')}}
                        </ul>
                    ` : ''}}
                    ${{jobs.ops_jobs.length > 0 ? `
                        <div>OPS Jobs:</div>
                        <ul style="margin: 2px 0 5px 20px; padding: 0;">
                            ${{jobs.ops_jobs.map(job => `<li>${{job}}</li>`).join('')}}
                        </ul>
                    ` : ''}}
                </div>
            `;
        }}

        // Filter out placeholder scripts from each list
        const filteredDirectCalls = Array.from(directCalls).filter(script => 
            scriptsData[script] && !scriptsData[script].isPlaceholder
        );
        const filteredCalledBy = Array.from(calledBy).filter(script => 
            scriptsData[script] && !scriptsData[script].isPlaceholder
        );
        const filteredIndirectCalls = Array.from(indirectCalls).filter(script => 
            scriptsData[script] && !scriptsData[script].isPlaceholder
        );
        const filteredIndirectCalledBy = Array.from(indirectCalledBy).filter(script => 
            scriptsData[script] && !scriptsData[script].isPlaceholder
        );

        // Get jobs for selected node
        const selectedNodeJobs = getNodeJobs(nodeId);

        return `
            <div style="margin-bottom: 20px; padding: 10px; border: 1px solid #ccc; border-radius: 5px;">
                <h4 style="margin-top: 0;">Selected: ${{nodeId}}</h4>
                ${{createJobsHTML(selectedNodeJobs)}}
                
                <div style="color: #FF0000; font-weight: bold; margin-top: 10px;">Directly Calls:</div>
                <ul style="list-style-type: none; padding-left: 10px; margin-top: 5px;">
                    ${{filteredDirectCalls.map(node => `
                        <li>
                            ${{node}}
                            ${{createJobsHTML(getNodeJobs(node))}}
                        </li>
                    `).join('')}}
                </ul>
                
                <div style="color: #FF0000; font-weight: bold; margin-top: 10px;">Called By:</div>
                <ul style="list-style-type: none; padding-left: 10px; margin-top: 5px;">
                    ${{filteredCalledBy.map(node => `
                        <li>
                            ${{node}}
                            ${{createJobsHTML(getNodeJobs(node))}}
                        </li>
                    `).join('')}}
                </ul>
                
                <div style="color: #FFA500; font-weight: bold; margin-top: 10px;">Indirectly Calls:</div>
                <ul style="list-style-type: none; padding-left: 10px; margin-top: 5px;">
                    ${{filteredIndirectCalls.map(node => `
                        <li>
                            ${{node}}
                            ${{createJobsHTML(getNodeJobs(node))}}
                        </li>
                    `).join('')}}
                </ul>
                
                <div style="color: #FFA500; font-weight: bold; margin-top: 10px;">Indirectly Called By:</div>
                <ul style="list-style-type: none; padding-left: 10px; margin-top: 5px;">
                    ${{filteredIndirectCalledBy.map(node => `
                        <li>
                            ${{node}}
                            ${{createJobsHTML(getNodeJobs(node))}}
                        </li>
                    `).join('')}}
                </ul>
            </div>
        `;
    }}

    // Function to get dependencies with placeholder handling
    function getDependencies(scriptId) {{
        let directCalls = new Set();
        let calledBy = new Set();
        let indirectCalls = new Set();
        let indirectCalledBy = new Set();

        // Ensure the script exists in scriptsData
        if (!scriptsData[scriptId]) {{
            console.log(`Creating placeholder for undefined script: ${{scriptId}}`);
            scriptsData[scriptId] = {{
                da2_jobs: [],
                ops_jobs: [],
                calls: [],
                isPlaceholder: true
            }};
        }}

        // Directly Calls
        scriptsData[scriptId].calls.forEach(calledScript => {{
            // Create placeholder if needed
            if (!scriptsData[calledScript]) {{
                console.log(`Creating placeholder for undefined direct call: ${{calledScript}}`);
                scriptsData[calledScript] = {{
                    da2_jobs: [],
                    ops_jobs: [],
                    calls: [],
                    isPlaceholder: true
                }};
            }}
            directCalls.add(calledScript);
        }});

        // Called By
        Object.keys(scriptsData).forEach(otherScript => {{
            if (scriptsData[otherScript].calls.includes(scriptId)) {{
                calledBy.add(otherScript);
            }}
        }});

        // Indirect Calls (depth 2)
        directCalls.forEach(function(directScript) {{
            // Create placeholder if needed
            if (!scriptsData[directScript]) {{
                console.log(`Creating placeholder for undefined direct script: ${{directScript}}`);
                scriptsData[directScript] = {{
                    da2_jobs: [],
                    ops_jobs: [],
                    calls: [],
                    isPlaceholder: true
                }};
            }}
            
            scriptsData[directScript].calls.forEach(indirectScript => {{
                // Create placeholder if needed
                if (!scriptsData[indirectScript]) {{
                    console.log(`Creating placeholder for undefined indirect call: ${{indirectScript}}`);
                    scriptsData[indirectScript] = {{
                        da2_jobs: [],
                        ops_jobs: [],
                        calls: [],
                        isPlaceholder: true
                    }};
                }}
                if (indirectScript !== scriptId && !directCalls.has(indirectScript)) {{
                    indirectCalls.add(indirectScript);
                }}
            }});
        }});

        // Indirect Called By (depth 2)
        calledBy.forEach(function(directCaller) {{
            Object.keys(scriptsData).forEach(otherScript => {{
                if (scriptsData[otherScript].calls.includes(directCaller) && 
                    otherScript !== scriptId && 
                    !calledBy.has(otherScript)) {{
                    indirectCalledBy.add(otherScript);
                }}
            }});
        }});

        return {{directCalls, calledBy, indirectCalls, indirectCalledBy}};
    }}

    // Function to update the selected nodes info box
    function updateInfoBox() {{
        let allNodesInfo = '';
        if (selectedNodes.size > 0) {{
            selectedNodes.forEach(nodeId => {{
                const connections = getDependencies(nodeId);
                allNodesInfo += createNodeInfoHTML(
                    nodeId,
                    connections.directCalls,
                    connections.calledBy,
                    connections.indirectCalls,
                    connections.indirectCalledBy
                );
            }});
        }} else {{
            allNodesInfo = '<p>No nodes selected</p>';
        }}
        document.getElementById('selectedNodesInfo').innerHTML = allNodesInfo;
    }}

    // Function to add a script and its dependencies to the network
    function addScript(scriptId) {{
        if (selectedNodes.has(scriptId)) {{
            alert('Script already added.');
            return;
        }}

        // Create a placeholder in scriptsData if the script doesn't exist
        if (!scriptsData[scriptId]) {{
            console.log(`Creating placeholder for undefined script: ${{scriptId}}`);
            scriptsData[scriptId] = {{
                da2_jobs: [],
                ops_jobs: [],
                calls: [],
                isPlaceholder: true
            }};
            return; // Don't add placeholder scripts
        }}

        // Add to selected nodes list in UI
        const selectedList = document.getElementById('selectedNodesList');
        const listItem = document.createElement('li');
        listItem.id = `selected-${{scriptId}}`;
        listItem.innerHTML = `
            ${{scriptId}}
            <button onclick="removeScript('{{scriptId}}')" 
                    style="margin-left: 10px; padding: 2px 5px; cursor: pointer;">
                Remove
            </button>
        `;
        selectedList.appendChild(listItem);

        // Traverse dependencies
        const connections = getDependencies(scriptId);

        // Direct Calls - Red
        connections.directCalls.forEach(calledScript => {{
            // Skip placeholder scripts
            if (!scriptsData[calledScript] || scriptsData[calledScript].isPlaceholder) {{
                return;
            }}

            if (!addedNodes.has(calledScript)) {{
                network.body.data.nodes.update([{{
                    id: calledScript, 
                    label: calledScript,
                    title: `${{calledScript}}\\nDA2 Jobs: ${{scriptsData[calledScript].da2_jobs.join(', ')}}\\nOPS Jobs: ${{scriptsData[calledScript].ops_jobs.join(', ')}}`,
                    color: '#97C2FC'
                }}]);
                addedNodes.add(calledScript);
            }}
            const edgeId = `${{scriptId}}->${{calledScript}}`;
            if (!addedEdges.has(edgeId)) {{
                network.body.data.edges.update([{{
                    from: scriptId, to: calledScript, id: edgeId, color: '#FF0000'
                }}]); // Red for direct
                addedEdges.add(edgeId);
            }}
        }});

        // Indirect Calls - Yellow
        connections.indirectCalls.forEach(indirectScript => {{
            // Skip placeholder scripts
            if (!scriptsData[indirectScript] || scriptsData[indirectScript].isPlaceholder) {{
                return;
            }}

            if (!addedNodes.has(indirectScript)) {{
                network.body.data.nodes.update([{{
                    id: indirectScript, 
                    label: indirectScript,
                    title: `${{indirectScript}}\\nDA2 Jobs: ${{scriptsData[indirectScript].da2_jobs.join(', ')}}\\nOPS Jobs: ${{scriptsData[indirectScript].ops_jobs.join(', ')}}`,
                    color: '#97C2FC'
                }}]);
                addedNodes.add(indirectScript);
            }}
            const edgeId = `${{scriptId}}->${{indirectScript}}`;
            if (!addedEdges.has(edgeId)) {{
                network.body.data.edges.update([{{
                    from: scriptId, to: indirectScript, id: edgeId, color: '#FFA500'
                }}]); // Yellow for indirect
                addedEdges.add(edgeId);
            }}
        }});

        // Called By - Red
        connections.calledBy.forEach(callingScript => {{
            // Skip placeholder scripts
            if (!scriptsData[callingScript] || scriptsData[callingScript].isPlaceholder) {{
                return;
            }}

            if (!addedNodes.has(callingScript)) {{
                network.body.data.nodes.update([{{
                    id: callingScript, 
                    label: callingScript,
                    title: `${{callingScript}}\\nDA2 Jobs: ${{scriptsData[callingScript].da2_jobs.join(', ')}}\\nOPS Jobs: ${{scriptsData[callingScript].ops_jobs.join(', ')}}`,
                    color: '#97C2FC'
                }}]);
                addedNodes.add(callingScript);
            }}
            const edgeId = `${{callingScript}}->${{scriptId}}`;
            if (!addedEdges.has(edgeId)) {{
                network.body.data.edges.update([{{
                    from: callingScript, to: scriptId, id: edgeId, color: '#FF0000'
                }}]); // Red for direct
                addedEdges.add(edgeId);
            }}
        }});

        // Indirect Called By - Yellow
        connections.indirectCalledBy.forEach(indirectCaller => {{
            // Skip placeholder scripts
            if (!scriptsData[indirectCaller] || scriptsData[indirectCaller].isPlaceholder) {{
                return;
            }}

            if (!addedNodes.has(indirectCaller)) {{
                network.body.data.nodes.update([{{
                    id: indirectCaller, 
                    label: indirectCaller,
                    title: `${{indirectCaller}}\\nDA2 Jobs: ${{scriptsData[indirectCaller].da2_jobs.join(', ')}}\\nOPS Jobs: ${{scriptsData[indirectCaller].ops_jobs.join(', ')}}`,
                    color: '#97C2FC'
                }}]);
                addedNodes.add(indirectCaller);
            }}
            const edgeId = `${{indirectCaller}}->${{scriptId}}`;
            if (!addedEdges.has(edgeId)) {{
                network.body.data.edges.update([{{
                    from: indirectCaller, to: scriptId, id: edgeId, color: '#FFA500'
                }}]); // Yellow for indirect
                addedEdges.add(edgeId);
            }}
        }});

        // Add the selected script itself (only if it's not a placeholder)
        if (!scriptsData[scriptId].isPlaceholder && !addedNodes.has(scriptId)) {{
            network.body.data.nodes.update([{{
                id: scriptId, 
                label: scriptId,
                title: `${{scriptId}}\\nDA2 Jobs: ${{scriptsData[scriptId].da2_jobs.join(', ')}}\\nOPS Jobs: ${{scriptsData[scriptId].ops_jobs.join(', ')}}`,
                color: '#97C2FC'
            }}]);
            addedNodes.add(scriptId);
        }}

        // Add to selected nodes
        selectedNodes.add(scriptId);

        // Highlight the node border
        network.body.data.nodes.update({{id: scriptId, borderWidth: 3, borderWidthSelected: 5}});

        // Update the info box
        updateInfoBox();
    }}

    // Function to remove a script and its dependencies from the network
    function removeScript(scriptId) {{
        if (!selectedNodes.has(scriptId)) {{
            console.log('Script not found:', scriptId);
            return;
        }}

        // Remove from selected nodes
        selectedNodes.delete(scriptId);

        // Remove from the UI list
        let listItem = document.getElementById(`selected-${{scriptId}}`);
        if (listItem) {{
            listItem.remove();
        }}

        // If there are no more selected nodes, clear everything
        if (selectedNodes.size === 0) {{
            network.body.data.nodes.clear();
            network.body.data.edges.clear();
            addedNodes.clear();
            addedEdges.clear();
            updateInfoBox();
            return;
        }}

        // Rebuild the network based on remaining selected nodes
        let nodesToKeep = new Set();
        let edgesToKeep = new Set();

        // For each remaining selected node, recalculate its dependencies
        selectedNodes.forEach(remainingScript => {{
            const connections = getDependencies(remainingScript);
            
            // Add all related nodes to keep
            nodesToKeep.add(remainingScript);
            connections.directCalls.forEach(script => nodesToKeep.add(script));
            connections.calledBy.forEach(script => nodesToKeep.add(script));
            connections.indirectCalls.forEach(script => nodesToKeep.add(script));
            connections.indirectCalledBy.forEach(script => nodesToKeep.add(script));

            // Rebuild edges for direct calls
            connections.directCalls.forEach(calledScript => {{
                edgesToKeep.add(`${{remainingScript}}->${{calledScript}}`);
            }});

            // Rebuild edges for indirect calls
            connections.indirectCalls.forEach(indirectScript => {{
                edgesToKeep.add(`${{remainingScript}}->${{indirectScript}}`);
            }});
        }});

        // Remove nodes that are no longer needed
        network.body.data.nodes.get().forEach(node => {{
            if (!nodesToKeep.has(node.id)) {{
                network.body.data.nodes.remove({{id: node.id}});
                addedNodes.delete(node.id);
            }}
        }});

        // Remove edges that are no longer needed
        network.body.data.edges.get().forEach(edge => {{
            const edgeId = `${{edge.from}}->${{edge.to}}`;
            if (!edgesToKeep.has(edgeId)) {{
                network.body.data.edges.remove({{id: edge.id}});
                addedEdges.delete(edgeId);
            }}
        }});

        // Update the info box
        updateInfoBox();
    }}

    // Function to reset all edge colors to default gray
    function resetEdgeColors() {{
        network.body.data.edges.get().forEach(function(edge) {{
            network.body.data.edges.update({{id: edge.id, color: {{color: '#848484'}}}});
        }});
    }}

    // Function to handle the Add Script button click
    document.getElementById('addScriptBtn').addEventListener('click', function() {{
        var input = document.getElementById('scriptSearchInput').value.trim();
        var searchType = document.getElementById('searchType').value;
        if (input !== '') {{
            let matchingScripts = new Set();
            if (searchType === 'name') {{
                // Direct name match
                Object.keys(scriptsData).forEach(scriptName => {{
                    if (scriptName.toLowerCase().includes(input.toLowerCase())) {{
                        matchingScripts.add(scriptName);
                    }}
                }});
            }} else if (searchType === 'da2') {{
                // DA2 job match
                Object.keys(scriptsData).forEach(scriptName => {{
                    scriptsData[scriptName].da2_jobs.forEach(job => {{
                        if (job.toLowerCase().includes(input.toLowerCase())) {{
                            matchingScripts.add(scriptName);
                        }}
                    }});
                }});
            }} else if (searchType === 'ops') {{
                // OPS job match
                Object.keys(scriptsData).forEach(scriptName => {{
                    scriptsData[scriptName].ops_jobs.forEach(job => {{
                        if (job.toLowerCase().includes(input.toLowerCase())) {{
                            matchingScripts.add(scriptName);
                        }}
                    }});
                }});
            }}

            if (matchingScripts.size > 0) {{
                matchingScripts.forEach(function(scriptId) {{
                    addScript(scriptId);
                }});
                document.getElementById('scriptSearchInput').value = '';
            }} else {{
                alert('No matching scripts found.');
            }}
        }}
    }});

    // Allow pressing Enter to add the script
    document.getElementById('scriptSearchInput').addEventListener('keydown', function(event) {{
        if (event.key === 'Enter') {{
            event.preventDefault();
            document.getElementById('addScriptBtn').click();
        }}
    }});

    // Function to handle dynamic datalist based on search type
    document.getElementById('searchType').addEventListener('change', function() {{
        var searchType = this.value;
        var dataList = document.getElementById('scriptList');
        var input = document.getElementById('scriptSearchInput').value.trim().toLowerCase();
        
        // Clear current datalist
        dataList.innerHTML = '';
        
        if (searchType === 'name') {{
            // For name search, show script names
            Object.keys(scriptsData).forEach(scriptName => {{
                if (scriptName.toLowerCase().includes(input)) {{
                    var option = document.createElement('option');
                    option.value = scriptName;
                    dataList.appendChild(option);
                }}
            }});
        }} else if (searchType === 'da2') {{
            // For DA2 search, show DA2 job names
            let uniqueDa2Jobs = new Set();
            Object.keys(scriptsData).forEach(scriptName => {{
                scriptsData[scriptName].da2_jobs.forEach(job => {{
                    if (job.toLowerCase().includes(input)) {{
                        uniqueDa2Jobs.add(job);
                    }}
                }});
            }});
            uniqueDa2Jobs.forEach(job => {{
                var option = document.createElement('option');
                option.value = job;
                dataList.appendChild(option);
            }});
        }} else if (searchType === 'ops') {{
            // For OPS search, show OPS job names
            let uniqueOpsJobs = new Set();
            Object.keys(scriptsData).forEach(scriptName => {{
                scriptsData[scriptName].ops_jobs.forEach(job => {{
                    if (job.toLowerCase().includes(input)) {{
                        uniqueOpsJobs.add(job);
                    }}
                }});
            }});
            uniqueOpsJobs.forEach(job => {{
                var option = document.createElement('option');
                option.value = job;
                dataList.appendChild(option);
            }});
        }}
    }});

    // Optional: Update datalist as user types
    document.getElementById('scriptSearchInput').addEventListener('input', function() {{
        document.getElementById('searchType').dispatchEvent(new Event('change'));
    }});

    // Function to handle network clicks
    network.on("click", function(params) {{
        if (params.nodes.length > 0) {{
            const clickedNode = params.nodes[0];
            
            // Toggle node selection
            if (selectedNodes.has(clickedNode)) {{
                removeScript(clickedNode);
            }} else {{
                addScript(clickedNode);
            }}
        }} else {{
            // Clicked on background, clear all selections
            selectedNodes.forEach(nodeId => {{
                removeScript(nodeId);
            }});
        }}
    }});

    // Add margin to the search box container
    const searchContainer = document.getElementById('search-container');
    searchContainer.style.marginBottom = '20px';  // Adds 20px margin below the search box


</script>
"""

# Combine the original HTML with custom HTML and JS
html_content = html_content.replace("</body>", custom_html + custom_js + "\n</body>")

# Write the updated HTML back to the file
with open("script_dependency_graph.html", "w", encoding="utf-8") as file:
    file.write(html_content)

print("Graph has been generated and saved to 'script_dependency_graph.html'. Open this file in your web browser to view the interactive graph.")


